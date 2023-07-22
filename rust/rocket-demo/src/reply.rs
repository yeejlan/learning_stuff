use std::io::Cursor;

use rocket::request::Request;
use rocket::response::{self, Response, Responder};
use rocket::http::{ContentType, Status};

use rocket::serde::json::serde_json::{Value, json};
use rocket::serde::Serialize;

use crate::exception::Exception;

use std::collections::BTreeMap;
use cached::proc_macro::once;

pub struct Reply(Value, i32);

#[once]
pub fn get_reply_map() -> BTreeMap<i32, &'static str> {
    Reply::get_map()
}

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
        let m = get_reply_map();
        m.get(&code).unwrap_or(&"none")
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

    pub fn result_success<T: Serialize>(resp: T) -> Result<Self, Exception> {
        Ok(Self::success(resp))
    }
    
    pub fn failed(message: &'static str, code: i32) -> Self {
        let data = json!({
            "code": code,
            "message": message,
            "reason": Reply::code_to_str(code),
            "data": None::<i32>,
        });
    
        Reply(data, code)
    }

    pub fn result_failed(message: &'static str, code: i32) -> Result<Self, Exception> {
        Ok(Self::failed(message, code))
    }

    pub fn result_exception(message: &'static str, code: i32) -> Result<Self, Exception> {
        Err(Exception::from((code, message)))
    }

    pub fn status_code(code: i32) -> u16 {
        let mut c: i32 = 200;
        if code >= 200 && code < 600 {
            c = code;
        }
        c as u16
    }

}

#[rocket::async_trait]
impl<'r> Responder<'r, 'static> for Reply {
    fn respond_to(self, _: &'r Request<'_>) -> response::Result<'static> {
        let json = self.0.to_string();
        Response::build()
            .status(Status::new(Reply::status_code(self.1)))
            .header(ContentType::JSON)
            .sized_body(json.len(), Cursor::new(json))
            .ok()
    }
}