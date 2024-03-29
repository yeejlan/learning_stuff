
use std::sync::atomic::{Ordering, AtomicU8, AtomicU16};
use tokio::io::{AsyncWriteExt, AsyncReadExt};
use tokio::process::{ChildStdout, ChildStdin};
use crate::exception::Exception;
use super::hippo::HippoMessage;

#[derive(Debug)]
pub struct HippoWorker {
    pub id: u32,
    pub child: tokio::process::Child,
    pub expire_at: i64,
    state: AtomicU8,
    job_counter: AtomicU16,
    stdin: ChildStdin,
    stdout: ChildStdout,
}

impl HippoWorker {
    const IDLE: u8 = 0;
    const PROCESSING: u8 = 1;
    const STOPPING: u8 = 2;
    pub fn new(id: u32, mut child: tokio::process::Child) -> Self {
        let stdin = child.stdin.take().unwrap();
        let stdout = child.stdout.take().unwrap();

        Self {
            id,
            child,
            state: AtomicU8::new(Self::IDLE),
            job_counter: AtomicU16::new(0),
            expire_at: 0,
            stdin,
            stdout,
        }
    }

    pub fn add_job_counter(&self) -> () {
        self.job_counter.fetch_add(1, Ordering::Relaxed); 
    }

    pub fn get_job_counter(&self) -> u16 {
        self.job_counter.load(Ordering::Relaxed)
    }

    pub fn reset_job_counter(&self) -> () {
        self.job_counter.store(0, Ordering::Relaxed);
    }

    pub fn next_expire_at(timeout_in_seconds: i64) -> i64 {
        let now = chrono::Utc::now();
        now.timestamp() + timeout_in_seconds
    }

    pub fn is_stopping(&self) -> bool {
        if self.state.load(Ordering::Relaxed) == Self::STOPPING {
            return true;
        }
        false
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
    
    pub fn to_idle(&self) -> () {
        self.state.store(Self::IDLE, Ordering::SeqCst)
    }

    pub fn to_stopping(&self) -> () {
        self.state.store(Self::STOPPING, Ordering::SeqCst)
    }

    pub async fn send_message(&mut self, msg: HippoMessage) -> Result<HippoMessage, Exception> {

        let payload = Self::encode_message(msg);

        self.stdin
            .write(&payload)
            .await?;
 
        self.stdin.flush().await?;
   

        let mut msg_header = vec![0; 8];
        let n = self.stdout.read(&mut msg_header).await?;
        if n != 8 {
            return Err("bad message header".into());
        }
        let kind: u32 = u32::from_be_bytes(msg_header[..4].try_into().unwrap());
        let msg_len: u32 = u32::from_be_bytes(msg_header[4..].try_into().unwrap());

        if msg_len > 5*1024*1024 {
            return Err("message too big".into());
        }

        let mut body = vec![0; msg_len as usize];
        let n = self.stdout.read(&mut body).await?;
        if n != msg_len as usize {
            return Err("bad message body".into());
        }

        let out = HippoMessage {
            kind,
            body,
        };

        Ok(out)

    }

    fn encode_message(msg: HippoMessage) -> Vec<u8> {

        let length = msg.body.len() as u32;
    
        let mut header = vec![0; 8];
        header[..4].copy_from_slice(&msg.kind.to_be_bytes());
        header[4..8].copy_from_slice(&length.to_be_bytes());
    
        let mut body = vec![];
        body.extend_from_slice(&header);
        body.extend_from_slice(&msg.body);
    
        body
    }    

}