use std::io::Cursor;

use rocket::request::Request;
use rocket::response::{self, Response, Responder};
use rocket::http::{ContentType, Status};

use rocket::serde::json::serde_json::{Value, json};
use rocket::serde::Serialize;

use crate::err_code;

pub struct Reply(Value, i32);

impl Reply {

    pub fn new(data: Value, code: i32) -> Self {
        Reply(data, code)
    }

    pub fn success<T: Serialize>(resp: T) -> Reply {
        let data = json!({
            "code": 0,
            "message": "success",
            "reason": "success",
            "data": resp,
        });
    
        Reply(data, 0)
    }
    
    pub fn failed(message: &'static str, code: i32) -> Reply {
        let data = json!({
            "code": code,
            "message": message,
            "reason": err_code::to_str(code),
            "data": None::<i32>,
        });
    
        Reply(data, code)
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
        dbg!(&json);
        Response::build()
            .status(Status::new(Reply::status_code(self.1)))
            .header(ContentType::JSON)
            .sized_body(json.len(), Cursor::new(json))
            .ok()
    }
}