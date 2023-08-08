
use std::sync::Arc;
use std::{collections::HashMap, process::Stdio};
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use flume::{Receiver, Sender};
use serde::Serialize;
use tokio::process::Command;
use tokio::sync::Semaphore;

use crate::err_wrap;
use crate::exception::Exception;

use super::worker::HippoWorker;

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
        let out_str = String::from_utf8_lossy(&self.msg_body).to_string();

        if self.msg_type == HippoMsgType::T_Response {
            return out_str.into_response();
        }
        
        (StatusCode::INTERNAL_SERVER_ERROR, out_str).into_response()
    }
}

pub struct HippoMsgType;

#[allow(non_upper_case_globals)]
impl HippoMsgType {

    pub const T_Request: u32 = 1;   //http request
    pub const T_Response: u32 = 2;  //http response
    pub const T_BadResponse: u32 = 3;   //error response

    pub const T_Ping: u32 = 101;
    pub const T_Pong: u32 = 102;
}

#[derive(Debug)]
pub struct HippoConfig {
    pub php_executor: String,
    pub worker_script: String,
    pub worker_num: u32,
    pub max_jobs_per_worker: u16,
    pub max_exec_time: u32,
}

impl HippoConfig {
    pub fn new() -> Self {
        Self { 
            php_executor: String::from("php"),
            worker_script: String::from("./hippo/worker.php"),
            worker_num: 8,
            max_jobs_per_worker: 500,
            max_exec_time: 60,
        }
    }

    pub fn set_php_executor(mut self, php_exec: String) -> Self {
        self.php_executor = php_exec;
        self
    }

    pub fn set_worker_script(mut self, script_path: String) -> Self {
        self.worker_script = script_path;
        self
    }

    pub fn set_worker_num(mut self, worker_num: u32) -> Self {
        self.worker_num = worker_num;
        self
    }  
    
    pub fn set_max_jobs_per_worker(mut self, max_jobs: u16) -> Self {
        self.max_jobs_per_worker = max_jobs;
        self
    }    

    pub fn set_max_exec_time(mut self, max_exec_time: u32) -> Self {
        self.max_exec_time = max_exec_time;
        self
    }    
}

#[derive(Debug)]
pub struct HippoPool {
    config: Arc<HippoConfig>,
    idle_worker_receiver: Receiver<HippoWorker>,
    idle_worker_sender: Sender<HippoWorker>,
    worker_permit: Semaphore,
}

impl HippoPool {

    pub fn new(config: Arc<HippoConfig>) -> Self {
        let worker_num = config.worker_num;

        let (idle_worker_sender, idle_worker_receiver) = 
            flume::bounded::<HippoWorker>(worker_num.try_into().unwrap());        

        //add idle workers
        for i in 0 .. worker_num {
            let worker = Self::new_worker(i+1, &config).unwrap();
            idle_worker_sender.send(worker).unwrap();
        }

        let worker_permit = Semaphore::new(worker_num.try_into().unwrap());

        Self {
            config,
            idle_worker_sender,
            idle_worker_receiver,
            worker_permit,
        }
    }

    pub fn add_idle_worker(self, worker: HippoWorker) {
        self.idle_worker_sender.send(worker).unwrap();
    }

    pub fn new_worker(worker_id: u32, config: &HippoConfig) -> Result<HippoWorker, Exception> {
        let child: tokio::process::Child = Command::new(&config.php_executor)
        .arg(&config.worker_script)
        .stdout(Stdio::piped())
        .stdin(Stdio::piped())
        // .stderr(Stdio::piped())
        .spawn()?;

        let worker = HippoWorker::new(worker_id, child);
        Ok(worker)
    }

    pub async fn send_message(&self, msg: HippoMessage) -> Result<HippoMessage, Exception> {
        //todo: add timeout

        let permit = self.worker_permit.acquire().await;

        let mut w = self.idle_worker_receiver.recv_async()
            .await
            .map_err(|e| err_wrap!("worker recv error", e))?;
        
        let res = w.send_message(msg).await;

        //release idle worker
        let renew_worker = Self::renew_worker(&self.config, w).unwrap();
        let sender = self.idle_worker_sender.clone();

        tokio::task::spawn_blocking(move || {
            sender.send(renew_worker).unwrap();
        });
     
        drop(permit);

        return Ok(res?);
    }

    pub fn renew_worker(config: &HippoConfig, w: HippoWorker) -> Result<HippoWorker, Exception> {

        let mut worker = w;

        //worker.add_job_counter();
        if worker.get_job_counter() >= config.max_jobs_per_worker {
            let worker_id = worker.id;
            let _ = worker.child.start_kill();

            let new_worker = Self::new_worker(worker_id, config);
            return new_worker;
        }

        Ok(worker)
    }


}
