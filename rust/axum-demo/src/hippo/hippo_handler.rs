
use std::collections::HashMap;

use axum::{Router, routing::post, extract::{Query, Path}, http::{HeaderMap, Method}};

use crate::{exception::Exception, reply::{self, Reply}};

use super::{hippo::{HippoRequest, HippoMessage, HippoMsgType}, get_hippo_pool};

pub fn build_router(mut r: Router) -> Router {
    r = r.route("/h/debug", post(hippo_status).get(hippo_status));
    r = r.route("/h/:a", post(hippo_handler).get(hippo_handler));
    r = r.route("/h/:a/:b", post(hippo_handler).get(hippo_handler));
    r = r.route("/h/:a/:b/:c", post(hippo_handler).get(hippo_handler));
    r
}

async fn hippo_status () -> Result<Reply, Exception> {
    let pool = get_hippo_pool();
    dbg!(pool);
    Reply::result_success("please check dbg message")
}

#[axum::debug_handler]
async fn hippo_handler (
    method: Method,
    headers: HeaderMap,
    Path(path): Path<Vec<String>>, 
    Query(query): Query<HashMap<String, String>>,
    body: String) -> reply::Result<HippoMessage>
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

    let payload = encode_request(HippoMsgType::T_Request, req);
    let pool = get_hippo_pool();
    let out = pool
        .send_message(payload)
        .await?;

    Ok(out)
}


fn encode_request(kind: u32, req: HippoRequest) -> HippoMessage {

    let body = serde_json::to_vec(&req).unwrap();

    HippoMessage {
        kind,
        body,
    }
}

