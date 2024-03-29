use actix_web::{HttpResponse, http::StatusCode};
use serde::Serialize;
use super::{err_code, exception::Exception};
use serde_json::{json, Value};

pub fn success<T: Serialize>(resp: T) -> Result<HttpResponse, Exception> {
    let data = json!({
        "code": 0,
        "message": "success",
        "reason": "success",
        "data": resp,
    });

    ok_result(data)
}

pub fn failed(message: &'static str, code: i32) -> Result<HttpResponse, Exception> {
    let data = json!({
        "code": code,
        "message": message,
        "reason": err_code::to_str(code),
        "data": None::<i32>,
    });    

    ok_result(data)
}

fn ok_result(data: Value) -> Result<HttpResponse, Exception> {
    Ok(HttpResponse::build(StatusCode::from_u16(200).unwrap())
    .json(data))
}