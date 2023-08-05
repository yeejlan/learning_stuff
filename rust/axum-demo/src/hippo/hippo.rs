use std::time::Duration;
use std::{collections::HashMap, process::Stdio};
use std::sync::atomic::{AtomicUsize, Ordering};
use serde::Serialize;
use tokio::process::Command;
use tokio::io::{AsyncWriteExt, AsyncReadExt};

use crate::err_wrap;
use crate::exception::Exception;

#[derive(Serialize, Debug)]
pub struct HippoRequest {
    pub method: String,
    pub path: String,      
    pub query: HashMap<String, String>,
    pub headers: HashMap<String, String>,
    pub body: String,
}

pub struct HippoWorker {
    pub child: tokio::process::Child,
    state: AtomicUsize,
    pub expire_at: i64,
}

impl HippoWorker {
    const IDLE: usize = 0;
    const PROCESSING: usize = 1;
    const STOPPING: usize = 2;
    pub fn new(child: tokio::process::Child) -> Self {
        Self {
            child,
            state: AtomicUsize::new(Self::IDLE),
            expire_at: 0,
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

    fn compare_and_swap(&self, current: usize, new: usize) -> Result<usize, ()> {
        self.state.compare_exchange(current, new, Ordering::SeqCst, Ordering::SeqCst)
            .map_err(|_| ())
    }

    pub fn into_processing(&self) -> Result<usize, ()> {
        self.compare_and_swap(Self::IDLE, Self::PROCESSING)
    }
    
    pub fn into_idle(&self) -> Result<usize, ()> {
        self.compare_and_swap(Self::PROCESSING, Self::IDLE)
    }

    pub fn into_stopping(&self) -> () {
        self.state.store(Self::STOPPING, Ordering::SeqCst)
    }

    pub async fn run_job(&mut self, payload: &[u8]) -> Result<Vec<u8>, Exception> {
        let child = &mut self.child;
        let mut stdin = child
        .stdin
        .take()
        .ok_or(Exception::from("get stdin error"))?;
    
        let mut stdout = child.stdout.take()
        .ok_or(Exception::from("get stdout error"))?;

        stdin
            .write(payload)
            .await
            .map_err(|e| err_wrap!("could not write to stdin", e))?;
    
        stdin.flush().await.map_err(|e| err_wrap!("flush stdin error", e))?;

        let mut buf = vec![0; 8];
        stdout.read_exact(&mut buf).await.unwrap();
        let _msg_type: u32 = u32::from_be_bytes(buf[..4].try_into().unwrap());
        let msg_len: u32 = u32::from_be_bytes(buf[4..].try_into().unwrap());
        let mut out = vec![0; msg_len.try_into().unwrap()];
        stdout.read_exact(&mut out).await.unwrap();
        Ok(out)
    }

}

pub struct HippoManager {
    php_executor: String,
    worker_script: String,    
    pool: Vec<HippoWorker>,
    worker_num: u32,
    max_exec_time: u32,
}

impl HippoManager {
    pub fn new() -> Self {
        Self { 
            php_executor: String::from("php"),
            worker_script: String::from("./hippo/worker.php"),
            pool: Vec::new(),
            worker_num: 4,
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
            .stderr(Stdio::piped())
            .spawn()
            .expect("failed to spawn php worker");

            let worker = HippoWorker::new(child);
            pool.push(worker);
        }

        self.pool = pool;
        self
    }

    pub async fn run_job(&mut self, payload: &[u8]) -> Result<Vec<u8>, Exception> {
        loop {
            for w in &mut self.pool {
                if w.is_idle() && w.into_processing().is_ok(){
                    return w.run_job(payload).await;
                }
            }
            tokio::time::sleep(Duration::from_millis(1)).await;
        }
    }

}

