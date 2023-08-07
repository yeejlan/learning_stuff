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
pub struct HippoPool {
    pub php_executor: String,
    pub worker_script: String,
    pub worker_num: u32,
    pub max_jobs_per_worker: u16,
    pub max_exec_time: u32,
    idle_worker_receiver: Receiver<HippoWorker>,
    idle_worker_sender: Sender<HippoWorker>,
    worker_permit: Semaphore,
}

impl HippoPool {
    pub fn new(worker_num: u32) -> Self {
        let (idle_worker_sender, idle_worker_receiver) = flume::bounded::<HippoWorker>(worker_num.try_into().unwrap());
        let worker_permit = Semaphore::new(worker_num.try_into().unwrap());
        Self { 
            php_executor: String::from("php"),
            worker_script: String::from("./hippo/worker.php"),
            worker_num,
            max_jobs_per_worker: 500,
            max_exec_time: 60,
            idle_worker_sender,
            idle_worker_receiver,
            worker_permit,
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

    pub fn set_max_jobs_per_worker(&mut self, max_jobs: u16) -> &mut Self {
        self.max_jobs_per_worker = max_jobs;
        self
    }    

    pub fn set_max_exec_time(&mut self, max_exec_time: u32) -> &mut Self {
        self.max_exec_time = max_exec_time;
        self
    }

    pub fn build(&mut self) -> &mut Self {

        for i in 0..self.worker_num {
            let child: tokio::process::Child = Command::new(&self.php_executor)
            .arg(&self.worker_script)
            .stdout(Stdio::piped())
            .stdin(Stdio::piped())
            // .stderr(Stdio::piped())
            .spawn()
            .expect("failed to spawn php worker");

            let worker = HippoWorker::new(i+1, child);
            self.idle_worker_sender.send(worker).unwrap();
        }

        self
    }

    pub async fn send_message(&self, msg: HippoMessage) -> Result<HippoMessage, Exception> {
        //todo: add timeout

        let permit = self.worker_permit.acquire().await;

        let mut w = self.idle_worker_receiver.recv_async()
            .await
            .map_err(|e| err_wrap!("worker recv error", e))?;
        
        w.add_job_counter();
        let res = w.send_message(msg).await;

        //release idle worker
        drop(permit);
        let sender = self.idle_worker_sender.clone();
        let max_jobs_per_worker = self.max_jobs_per_worker;
        let php_executor = self.php_executor.to_owned();
        let worker_script = self.worker_script.to_owned();
        tokio::spawn(async move {
            //renew worker
            let mut worker = w;
            if worker.get_job_counter() >= max_jobs_per_worker {
                let worker_id = worker.id;
                worker.child.kill().await
                    .expect("failed to kill php worker");
    
                let child: tokio::process::Child = Command::new(php_executor)
                    .arg(worker_script)
                    .stdout(Stdio::piped())
                    .stdin(Stdio::piped())
                    // .stderr(Stdio::piped())
                    .spawn()
                    .expect("failed to spawn php worker");

                worker = HippoWorker::new(worker_id, child);
            }

            if let Err(e) = sender.send_async(worker)
            .await {
                tracing::error!("failed to send idle worker: {:?}", e);
            }
        });

        return Ok(res?);
    }

    // pub async fn renew_worker(&self, mut w: HippoWorker) -> Result<HippoWorker, Exception> {

    //     let mut worker = w;

    //     if worker.get_job_counter() >= self.max_jobs_per_worker {
    //         let worker_id = w.id;
    //         w.child.kill().await
    //             .map_err(|e| err_wrap!("kill worker error", e))?;

    //         let child: tokio::process::Child = Command::new(&self.php_executor)
    //         .arg(&self.worker_script)
    //         .stdout(Stdio::piped())
    //         .stdin(Stdio::piped())
    //         // .stderr(Stdio::piped())
    //         .spawn()
    //         .expect("failed to spawn php worker");
    //         let worker = HippoWorker::new(worker_id, child);
    //         return Ok(worker);
    //     }

    //     Ok(w)
    // }


}
