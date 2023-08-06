use std::time::Duration;
use std::{collections::HashMap, process::Stdio};
use std::sync::atomic::{Ordering, AtomicU8};
use axum::response::{IntoResponse, Response};
use serde::Serialize;
use tokio::process::{Command, ChildStdin, ChildStdout};
use tokio::io::{AsyncWriteExt, AsyncReadExt};

use crate::exception::Exception;
use crate::reply::Reply;

#[derive(Serialize, Debug)]
pub struct HippoRequest {
    pub method: String,
    pub path: String,      
    pub query: HashMap<String, String>,
    pub headers: HashMap<String, String>,
    pub body: String,
}

pub struct HippoMessage {
    pub msg_type: u32,
    pub msg_body: Vec<u8>,
}


impl IntoResponse for HippoMessage {
    fn into_response(self) -> Response {
        if self.msg_type == HippoMsgType::T_Response {
            let out_str = String::from_utf8_lossy(&self.msg_body).to_string();

            return out_str.into_response();
        }
        
        Reply::failed("bad result", Reply::BAD_RESULT)
            .into_response()
    }
}

pub struct HippoMsgType;

#[allow(non_upper_case_globals)]
impl HippoMsgType {

    pub const T_Request: u32 = 1;   //mgspack request
    pub const T_Response: u32 = 2;  //mgspack response
    pub const T_BadResponse: u32 = 3;   //error response

    pub const T_Ping: u32 = 101;
    pub const T_Pong: u32 = 102;
}

#[derive(Debug)]
pub struct HippoWorker {
    pub child: tokio::process::Child,
    pub expire_at: i64,
    state: AtomicU8,
    stdin: ChildStdin,
    stdout: ChildStdout,
}

impl HippoWorker {
    const IDLE: u8 = 0;
    const PROCESSING: u8 = 1;
    const STOPPING: u8 = 2;
    pub fn new(mut child: tokio::process::Child) -> Self {
        let stdin = child.stdin.take().unwrap();
        let stdout = child.stdout.take().unwrap();
        Self {
            child,
            state: AtomicU8::new(Self::IDLE),
            expire_at: 0,
            stdin,
            stdout,
        }
    }

    pub fn next_expire_at(timeout_in_seconds: i64) -> i64 {
        let now = chrono::Utc::now();
        now.timestamp() + timeout_in_seconds
    }

    pub fn is_idle(&self) -> bool {
        if self.state.load(Ordering::Relaxed) == Self::IDLE {
            return true;
        }
        false
    }

    fn compare_and_swap(&self, current: u8, new: u8) -> Result<u8, ()> {
        self.state.compare_exchange(current, new, Ordering::SeqCst, Ordering::SeqCst)
            .map_err(|_| ())
    }

    pub fn into_processing(&self) -> Result<u8, ()> {
        self.compare_and_swap(Self::IDLE, Self::PROCESSING)
    }
    
    pub fn into_idle(&self) -> () {
        self.state.store(Self::IDLE, Ordering::SeqCst)
    }

    pub fn into_stopping(&self) -> () {
        self.state.store(Self::STOPPING, Ordering::SeqCst)
    }

    pub async fn send_message(&mut self, msg: HippoMessage) -> Result<HippoMessage, Exception> {
        //set timeout
        self.expire_at = Self::next_expire_at(60);

        // let child = &mut self.child;
        // let mut stdin = child
        // .stdin
        // .take()
        // .ok_or(Exception::from("get stdin error"))?;
    
        // let mut stdout = child.stdout.take()
        // .ok_or(Exception::from("get stdout error"))?;

        let payload = Self::encode_message(msg);

        self.stdin
            .write(&payload)
            .await?;
 
        self.stdin.flush().await?;
   

        let mut msg_header = vec![0; 8];
        self.stdout.read_exact(&mut msg_header).await?;
        let msg_type: u32 = u32::from_be_bytes(msg_header[..4].try_into().unwrap());
        let msg_len: u32 = u32::from_be_bytes(msg_header[4..].try_into().unwrap());
        let mut msg_body = vec![0; msg_len.try_into().unwrap()];
        self.stdout.read_exact(&mut msg_body).await?;

        let out = HippoMessage {
            msg_type,
            msg_body,
        };

        Ok(out)
    }

    fn encode_message(msg: HippoMessage) -> Vec<u8> {

        let length = msg.msg_body.len() as u32;
    
        let mut header = vec![0; 8];
        header[..4].copy_from_slice(&msg.msg_type.to_be_bytes());
        header[4..8].copy_from_slice(&length.to_be_bytes());
    
        let mut body = vec![];
        body.extend_from_slice(&header);
        body.extend_from_slice(&msg.msg_body);
    
        body
    }    

}

#[derive(Debug)]
pub struct HippoPool {
    pub php_executor: String,
    pub worker_script: String,    
    pub pool: Vec<HippoWorker>,
    pub worker_num: u32,
    pub max_exec_time: u32,
}

impl HippoPool {
    pub fn new() -> Self {
        let worker_num = 4;
        Self { 
            php_executor: String::from("php"),
            worker_script: String::from("./hippo/worker.php"),
            pool: Vec::new(),
            worker_num,
            max_exec_time: 60,
        }
    }

    pub fn set_php_executor(&mut self, php_exec: String) -> &mut Self {
        self.php_executor = php_exec;
        self
    }

    pub fn set_worker_script(&mut self, script_path: String) -> &mut Self {
        self.worker_script = script_path;
        self
    }

    pub fn set_worker_num(&mut self, worker_num: u32) -> &mut Self {
        self.worker_num = worker_num;
        self
    }

    pub fn set_max_exec_time(&mut self, max_exec_time: u32) -> &mut Self {
        self.max_exec_time = max_exec_time;
        self
    }

    pub fn build(&mut self) -> &mut Self {

        let mut pool = Vec::new();

        for _ in 0..self.worker_num {
            let child: tokio::process::Child = Command::new(&self.php_executor)
            .arg(&self.worker_script)
            .stdout(Stdio::piped())
            .stdin(Stdio::piped())
            // .stderr(Stdio::piped())
            .spawn()
            .expect("failed to spawn php worker");

            let worker = HippoWorker::new(child);
            pool.push(worker);
        }

        self.pool = pool;
        self
    }

    pub async fn send_message(&mut self, msg: HippoMessage) -> Result<HippoMessage, Exception> {
        //todo: add timeout and spawn and max queue using tokio::sync::Semaphore
        loop {
            for w in &mut self.pool {
                if w.is_idle() && w.into_processing().is_ok(){
                    let res = w.send_message(msg).await;
                    w.into_idle(); 
                    return Ok(res?);
                }
            }
            tokio::time::sleep(Duration::from_millis(1)).await;
            return Err("all worker is busy".into());
        }
    }

}

