
use axum::{response::{IntoResponse,Response}, http::StatusCode};
use once_cell::sync::Lazy;
use serde_json::{Value, json};
use serde::Serialize;

use crate::exception::Exception;

use std::collections::BTreeMap;

pub struct Reply(Value, i32);
pub type Result<T> = std::result::Result<T, Exception>;

static MAP: Lazy<BTreeMap<i32, &'static str>> = Lazy::new(|| {
    Reply::get_map()
});

impl Reply {

    //error kind
    pub const USER_EXCEPTION: i32 = -1000;
    pub const MODEL_EXCEPTION: i32 = -2000;
    pub const SERVICE_EXCEPTION: i32 = -3000;
    pub const FLUX_EXCEPTION: i32 = -4000;

    //error code
    pub const SUCCESS: i32 = 0;
    pub const BAD_RESULT: i32 = 1000;
    pub const BAD_TOKEN: i32 = 1100;
    pub const BAD_PARAM: i32 = 1200;
    pub const OPERATION_NOT_ALLOWED: i32 = 1300;
    pub const RESOURCE_NOT_FOUND: i32 = 1400;
    pub const OPERATION_FAILED: i32 = 1500;
    pub const OPERATION_PENDING: i32 = 1600;    

    pub fn new(data: Value, code: i32) -> Self {
        Reply(data, code)
    }

    pub fn get_map() -> BTreeMap<i32, &'static str> {
        BTreeMap::from([
            (401, "unauthorized"),
            (403, "forbidden"),
            (404, "not_found"),
            (405, "method_not_allowed"),
            (500, "internal_server_error"),
    
            (Self::SUCCESS, "success"),
            (Self::BAD_RESULT, "bad_result"),
            (Self::BAD_TOKEN, "bad_token"),
            (Self::BAD_PARAM, "bad_param"),
            (Self::OPERATION_NOT_ALLOWED, "operation_not_allowed"),
            (Self::RESOURCE_NOT_FOUND, "resource_not_found"),
            (Self::OPERATION_FAILED, "operation_failed"),
            (Self::OPERATION_PENDING, "operation_pending"),
        ])
    }    

    pub fn code_to_str(code: i32) -> &'static str {
        MAP.get(&code).unwrap_or(&"none")
    }
    
    pub fn code_to_kind(code: i32) -> i32 {
        if code >= 1000 {
            return Self::USER_EXCEPTION;
        }
        code - (code % 1000)
    }    

    pub fn success<T: Serialize>(resp: T) -> Self {
        let data = json!({
            "code": 0,
            "message": "success",
            "reason": "success",
            "data": resp,
        });
    
        Reply(data, 0)
    }

    pub fn result_success<T: Serialize>(resp: T) -> Result<Self> {
        Ok(Self::success(resp))
    }
    
    pub fn failed(message: &str, code: i32) -> Self {
        let data = json!({
            "code": code,
            "message": message,
            "reason": Reply::code_to_str(code),
            "data": None::<i32>,
        });
    
        Reply(data, code)
    }

    pub fn result_failed(message: &str, code: i32) -> Result<Self> {
        Ok(Self::failed(message, code))
    }

    pub fn result_error(message: &str, code: i32) -> Result<Self> {
        Err(Exception::from((code, message)))
    }

    pub fn status_code(code: i32) -> u16 {
        let mut c: i32 = 200;
        //Status code values in the range 100-999 (inclusive) are supported
        if code >= 100 && code < 1000 {
            c = code;
        }
        c as u16
    }

}

impl IntoResponse for Reply {
    fn into_response(self) -> Response {
        
        let json = self.0.to_string();
        let code = Self::status_code(self.1);
        (
            StatusCode::from_u16(code).unwrap(),
            [("content-type", "application/json")],
            json
        ).into_response()
    }
}
