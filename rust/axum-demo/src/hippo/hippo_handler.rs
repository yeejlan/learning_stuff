
use std::{collections::HashMap, process::Stdio};

use axum::{Router, routing::post, extract::{Query, Path}, http::{HeaderMap, Method}};

use crate::{exception::Exception, err_wrap};

use super::hippo::HippoRequest;
use tokio::io::AsyncWriteExt;
use tokio::process::Command;

pub fn build_router(mut r: Router) -> Router {
    r = r.route("/h/:a", post(hippo_handler).get(hippo_handler));
    r = r.route("/h/:a/:b", post(hippo_handler).get(hippo_handler));
    r = r.route("/h/:a/:b/:c", post(hippo_handler).get(hippo_handler));
    r
}

async fn hippo_handler(
    method: Method,
    headers: HeaderMap,
    Path(path): Path<Vec<String>>, 
    Query(query): Query<HashMap<String, String>>,
    body: String) -> Result<String, Exception>
{

    let path = path.join("/");

    let mut header_map = HashMap::new();
    for (key, value) in headers.iter() {
        header_map.insert(key.as_str().to_string(), 
            value.to_str().unwrap_or("").to_string());
    }

    let req = HippoRequest {
        method: method.to_string(),
        path,
        query,
        headers: header_map,
        body,
    };

    let mut child = Command::new("php")
        .arg("./hippo/worker.php")
        .stdout(Stdio::piped())
        .stdin(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("failed to spawn command");    

    let mut stdin = child
    .stdin
    .take()
    .expect("child did not have a handle to stdin");

    let msg = encode_request(1, req);
    stdin
        .write(&msg)
        .await
        .expect("could not write to stdin");

    stdin.flush().await.map_err(|e| err_wrap!("flush error", e))?;

    let out = child.wait_with_output()
        .await
        .map_err(|e| err_wrap!("read stdout error", e))?;

    let response = String::from_utf8_lossy(&out.stdout).into_owned();

    Ok(response)
}

fn encode_request(msg_type: u32, req: HippoRequest) -> Vec<u8> {

    let encoded = rmp_serde::to_vec(&req).unwrap();

    let length = encoded.len() as u32;

    let mut header = vec![0; 8];
    header[..4].copy_from_slice(&msg_type.to_be_bytes());
    header[4..8].copy_from_slice(&length.to_be_bytes());

    let mut body = vec![];
    body.extend_from_slice(&header);
    body.extend_from_slice(&encoded);

    body
}