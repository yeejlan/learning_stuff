use std::time::Duration;
use std::{collections::HashMap, process::Stdio};
use std::sync::atomic::{AtomicUsize, Ordering, AtomicU32};
use serde::Serialize;
use tokio::process::Command;

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
    pub client: tokio::process::Child,
    pub state: WorkerState,
    pub session: SessionGenerator,
    pub expire_at: i64,
}

impl HippoWorker {
    pub fn new(client: tokio::process::Child) -> Self {
        Self {
            client,
            state: WorkerState::new(),
            session: SessionGenerator::new(),
            expire_at: 0,
        }
    }

    pub fn next_expire_at(timeout_in_seconds: i64) -> i64 {
        let now = chrono::Utc::now();
        now.timestamp() + timeout_in_seconds
    }
}

pub struct WorkerState {
    state: AtomicUsize,
}

impl WorkerState {
    const IDLE: usize = 0;
    const PROCESSING: usize = 1;

    pub fn new() -> Self {
        Self { 
            state: AtomicUsize::new(Self::IDLE),
        }
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

    pub fn set_processing(&self) -> Result<usize, ()> {
        self.compare_and_swap(Self::IDLE, Self::PROCESSING)
    }
    
    pub fn set_idle(&self) -> Result<usize, ()> {
        self.compare_and_swap(Self::PROCESSING, Self::IDLE)
    }
}

pub struct SessionGenerator {
    counter: AtomicU32,
}

impl SessionGenerator {
    pub fn new() -> Self {
        Self { 
            counter: AtomicU32::new(1),
        }
    }

    pub fn next_session_id(&self) -> u32 {
        self.counter.fetch_add(1, Ordering::Relaxed)
    }
}

pub struct HippoManager {
    php_executor: String,
    worker_script: String,    
    pool: Vec<HippoWorker>,
    max_workers: u32,
    max_exec_time: u32,
}

impl HippoManager {
    pub fn new() -> Self {
        Self { 
            php_executor: String::from("php"),
            worker_script: String::from("./hippo/worker.php"),
            pool: Vec::new(),
            max_workers: 4,
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

    pub fn set_max_workers(mut self, max_workers: u32) -> Self {
        self.max_workers = max_workers;
        self
    }

    pub fn set_max_exec_time(mut self, max_exec_time: u32) -> Self {
        self.max_exec_time = max_exec_time;
        self
    }

    pub fn build(mut self) -> Self {

        let mut pool = self.pool;

        for _ in 0..self.max_workers {
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

    pub async fn run_job(self) -> Result<Vec<u8>, Exception> {
        loop {
            for w in self.pool {
                if w.state.is_idle() && w.state.set_processing().is_ok(){
                    return w.run_job(xxx).await?;
                }
            }
            tokio::time::sleep(Duration::from_millis(1));
        }
    }

}

