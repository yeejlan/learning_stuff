
use actix_web::{web::{self, Bytes}, get, post, Responder, HttpResponse};
use serde::{Serialize, Deserialize};
use serde_json::json;

use crate::{ext::{exception::Exception, reply, err_code, request_id::RequestId}, err_wrap};

pub fn service_config(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/test")
        .service(action_err)
        .service(action_failed)
        .service(action_raw_body)
        .service(action_submit)
        .service(action_err500)
        .service(action_err_chain)
    );
}

#[derive(Serialize, Deserialize, Debug)]
struct SubmitParams {
    username: String,
    aka: Option<String>,
}

#[post("/submit")]
async fn action_submit(id: RequestId, params: web::Json<SubmitParams>) -> Result<impl Responder, Exception> {
    reply::success(json!({
        "id": id.to_string(),
        "params": params,
    }))
}

#[post("/raw-body")]
async fn action_raw_body(bytes: Bytes) -> Result<impl Responder, Exception> {
    let bodystr = String::from_utf8(bytes.to_vec())
        .map_err(|e| (err_code::BAD_RESULT, e.to_string()))?;

    tracing::info!(bodystr);
    reply::success(json!({
        "bodystr": bodystr,
    }))
}

#[get("/err")]
async fn action_err() -> Result<HttpResponse, Exception> {
    Err((401, "no permission"))?
}

#[get("/failed")]
async fn action_failed() -> Result<impl Responder, Exception> {
    reply::failed("my testing error", err_code::OPERATION_NOT_ALLOWED)
}

#[get("/err500")]
async fn action_err500() -> Result<impl Responder, Exception> {
    let b = vec![0, 159, 146, 150];
    String::from_utf8(b)
        .map_err(|e| err_wrap!(e))?;
    Ok("SUCCESS~")
}

#[get("/err-chain")]
async fn action_err_chain() -> Result<impl Responder, Exception> {
    let s = get_my_string()
        .await
        .map_err(|e| err_wrap!("My testing error!", e))?;
    Ok(s)
}

async fn _may_throw_error() -> Result<String, Exception> {
    let b = vec![0, 159, 146, 150];
    let s = String::from_utf8(b)
        .map_err(|e| err_wrap!("_may_throw_error failed!".to_owned(), e))?;

    Ok(s)
}

async fn get_my_string() -> Result<String, Exception> {
    let s = _may_throw_error()
        .await
        .map_err(|e| err_wrap!(err_code::OPERATION_FAILED, "get_my_string failed", e))?;
    Ok(s)
}