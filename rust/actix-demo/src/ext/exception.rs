
use actix_web::{ResponseError, http::StatusCode, HttpResponse};

use super::err_code;
use serde_json::json;

#[macro_export]
macro_rules! err_wrap { 
    ($e:expr) => {
        err_wrap!(500, "", $e)
    };
    ($msg:expr, $e:expr) => {
        err_wrap!(500, $msg, $e)
    };
    ($code:expr, $msg:expr, $e:expr) => {{

        let type_name = $crate::ext::exception::get_type_of(&$e);
        let mut c = Vec::new();
        let mut m = format!("{}", $msg);
        if m.trim().is_empty() {
            m = format!("{}", type_name);
        }
        c.push(format!("{}: {} @{}:{}", type_name, $e, file!(), line!()));
        let e_any = &$e as &dyn std::any::Any;
        if let Some(ex) = e_any.downcast_ref::<Exception>() {
            c.extend(ex.cause.to_owned());
        }

        Exception{
            code: $code,
            message: m,
            cause: c,
        }
    }};
}

pub fn get_type_of<T>(_: T) -> &'static str {
    let n = std::any::type_name::<T>()
        .trim_start_matches('&');
    if n == "str" || n == "String" {
        return "Error";
    }
    if n.find("::").is_some() {
        let n_arr: Vec<&str> = n.split("::").collect();
        return n_arr.last().unwrap();
    }
    n
}

#[derive(Debug, serde::Serialize, Default)]
pub struct Exception {
    pub code: i32,
    pub message: String,
    pub cause: Vec<String>,
}

impl From<String> for Exception {
    fn from(e: String) -> Self {
        Self{code:500, message:e, ..Default::default()}
    }
}

impl From<&str> for Exception {
    fn from(e: &str) -> Self {
        Self{code:500, message:e.to_string(), ..Default::default()}
    }
}

impl From<(i32, String)> for Exception {
    fn from(e: (i32, String)) -> Self {
        Self{code:e.0, message:e.1, ..Default::default()}
    }
}

impl From<(i32, &str)> for Exception {
    fn from(e: (i32, &str)) -> Self {
        Self{code:e.0, message:e.1.to_owned(), ..Default::default()}
    }
}

impl From<(String, String)> for Exception {
    fn from(e: (String, String)) -> Self {
        Self{
            code: 500, 
            message: e.0,
            cause: vec![e.1],
        }
    }
}

impl From<(String, &str)> for Exception {
    fn from(e: (String, &str)) -> Self {
        Self{
            code: 500, 
            message: e.0,
            cause: vec![e.1.to_owned()],
        }
    }
}

impl From<(&str, String)> for Exception {
    fn from(e: (&str, String)) -> Self {
        Self{
            code: 500, 
            message: e.0.to_owned(),
            cause: vec![e.1],
        }
    }
}

impl From<(&str, &str)> for Exception {
    fn from(e: (&str, &str)) -> Self {
        Self{
            code: 500, 
            message: e.0.to_owned(),
            cause: vec![e.1.to_owned()],
        }
    }
}

impl From<(i32, String, String)> for Exception {
    fn from(e: (i32, String, String)) -> Self {
        Self{
            code: e.0, 
            message: e.1,
            cause: vec![e.2],
        }
    }
}

impl From<(i32, String, &str)> for Exception {
    fn from(e: (i32, String, &str)) -> Self {
        Self{
            code: e.0, 
            message: e.1,
            cause: vec![e.2.to_owned()],
        }
    }
}

impl From<(i32, &str, String)> for Exception {
    fn from(e: (i32, &str, String)) -> Self {
        Self{
            code: e.0, 
            message: e.1.to_owned(),
            cause: vec![e.2],
        }
    }
}

impl From<(i32, &str, &str)> for Exception {
    fn from(e: (i32, &str, &str)) -> Self {
        Self{
            code: e.0, 
            message: e.1.to_owned(),
            cause: vec![e.2.to_owned()],
        }
    }
}


impl From<serde_json::Error> for Exception {
    fn from(e: serde_json::Error) -> Self {
        Self{code:500, message: format!("Json encode error: {}", e), ..Default::default()}
    }
}

impl std::error::Error for Exception {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        None
    }
}

impl std::fmt::Display for Exception {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Exception{code, message, cause: _} => 
                write!(f, "[{}] {}", code, message),
        }
    }
}


impl ResponseError for Exception {
    fn status_code(&self) -> StatusCode {
        let mut code: i32 = 1000;
        if self.code > 0 && self.code < 1000 {
            code = self.code;
        }
        if self.code >= 1000 {
            code = 200;
        }
        StatusCode::from_u16(code as u16).unwrap()
    }

    fn error_response(&self) -> HttpResponse {
        //don't log http response code, except 500
        if self.code>0 && self.code<1000 && self.code !=500 {
            //pass
        }else{
            tracing::error!("{}, cause: {:#?}", self.message, self.cause);
        }

        let data = json!({
            "code": self.code,
            "message": self.message.clone(),
            "reason": err_code::to_str(self.code).to_string(),
            "trace": self.cause,
            "data": None::<i32>
        });
        HttpResponse::build(self.status_code())
            .json(data)
    }    
}
