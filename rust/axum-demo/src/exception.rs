
use axum::{response::{IntoResponse, Response}, http::StatusCode};
use serde_json::json;
use crate::reply::Reply;

///    Creates an Exception from any error, capturing the error chain.
///    
///    This allows wrapping any error into an Exception
///    while preserving the cause chain for debugging.
///
///    # Examples
///    ```
///    let e = err_wrap!(io::Error::new(ErrorKind::Timeout)); //code = 500
/// 
///    let e = err_wrap!("Internal Error", io::Error::new(ErrorKind::FileNotExist)); //code = 500
/// 
///    let e = err_wrap!(403, "Forbidden", io::Error::new(ErrorKind::PermissionDenied));
/// 
///    let e = err_wrap!(Reply::OPERATION_FAILED, "Get user info failed", io::Error::new(ErrorKind::NotFound));
///    ```
/// 
///    Useful for central handling of errors from different sources.
#[macro_export]
macro_rules! err_wrap { 
 
    ($e:expr) => {
        err_wrap!(500, "", $e)
    };
    ($msg:expr, $e:expr) => {
        err_wrap!(500, $msg, $e)
    };
    ($code:expr, $msg:expr, $e:expr) => {{

        let type_name = $crate::exception::get_type_of(&$e);
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
            root: Some(Box::new($e)),
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

#[derive(Debug, Default)]
pub struct Exception {
    pub code: i32,
    pub message: String,
    pub cause: Vec<String>,
    pub root: Option<Box<dyn std::error::Error>>,
}

pub type Result<T> = std::result::Result<T, Exception>;

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

impl From<(String, i32)> for Exception {
    fn from(e: (String, i32)) -> Self {
        Self{code:e.1, message:e.0, ..Default::default()}
    }
}

impl From<(&str, i32)> for Exception {
    fn from(e: (&str, i32)) -> Self {
        Self{code:e.1, message:e.0.to_owned(), ..Default::default()}
    }
}

impl From<(String, String)> for Exception {
    fn from(e: (String, String)) -> Self {
        Self{
            code: 500, 
            message: e.0,
            cause: vec![e.1],
            root: None,
        }
    }
}

impl From<(String, &str)> for Exception {
    fn from(e: (String, &str)) -> Self {
        Self{
            code: 500, 
            message: e.0,
            cause: vec![e.1.to_owned()],
            root: None,
        }
    }
}

impl From<(&str, String)> for Exception {
    fn from(e: (&str, String)) -> Self {
        Self{
            code: 500, 
            message: e.0.to_owned(),
            cause: vec![e.1],
            root: None,
        }
    }
}

impl From<(&str, &str)> for Exception {
    fn from(e: (&str, &str)) -> Self {
        Self{
            code: 500, 
            message: e.0.to_owned(),
            cause: vec![e.1.to_owned()],
            root: None,
        }
    }
}

impl From<(i32, String, String)> for Exception {
    fn from(e: (i32, String, String)) -> Self {
        Self{
            code: e.0, 
            message: e.1,
            cause: vec![e.2],
            root: None,
        }
    }
}

impl From<(i32, String, &str)> for Exception {
    fn from(e: (i32, String, &str)) -> Self {
        Self{
            code: e.0, 
            message: e.1,
            cause: vec![e.2.to_owned()],
            root: None,
        }
    }
}

impl From<(i32, &str, String)> for Exception {
    fn from(e: (i32, &str, String)) -> Self {
        Self{
            code: e.0, 
            message: e.1.to_owned(),
            cause: vec![e.2],
            root: None,
        }
    }
}

impl From<(i32, &str, &str)> for Exception {
    fn from(e: (i32, &str, &str)) -> Self {
        Self{
            code: e.0, 
            message: e.1.to_owned(),
            cause: vec![e.2.to_owned()],
            root: None,
        }
    }
}

impl From<std::io::Error> for Exception {
    fn from(e: std::io::Error) -> Self {
        Self{
            code:500, 
            message: format!("io error: {}", e),
            root: Some(Box::new(e)),
            ..Default::default()
        }
    }
}

impl From<serde_json::Error> for Exception {
    fn from(e: serde_json::Error) -> Self {
        Self{
            code:500, 
            message: format!("serde_json error: {}", e),
            root: Some(Box::new(e)),
            ..Default::default()
        }
    }
}

impl From<pyo3::PyErr> for Exception {
    fn from(e: pyo3::PyErr) -> Self {
        Self{
            code:500, 
            message: format!("python error: {}", e),
            root: Some(Box::new(e)),
            ..Default::default()
        }
    }
}

// impl From<sqlx::Error> for Exception {
//     fn from(e: sqlx::Error) -> Self {
//         Self {
//             code:500,
//             message: format!("sqlx error: {}", e), 
//             root: Some(Box::new(e)),
//             ..Default::default()
//         }
//     }
// }

impl std::error::Error for Exception {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        None
    }
}

impl std::fmt::Display for Exception {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Exception{code, message, cause: _, root: _} => 
                write!(f, "[{}] {}", code, message),
        }
    }
}

impl IntoResponse for Exception {
    fn into_response(self) -> Response {

        //log internal server error
        if self.code ==500 {

            let mut buffer = String::new();
            buffer.push_str(&self.message);
            buffer.push_str("\n");
            for line in &self.cause {
                buffer.push_str(line);
                buffer.push_str("\n");
            }
            tracing::error!("{}", buffer);
        }

        let payload = json!({
            "code": self.code,
            "message": self.message,
            "reason": Reply::code_to_str(self.code),
            "data": None::<i32>,
            "trace": self.cause,
            // "root": self.root.unwrap_or("none".into()).to_string(),
            "data": None::<i32>            
        });
    
        let json = payload.to_string();

        let code = Reply::status_code(self.code);
        (
            StatusCode::from_u16(code).unwrap(),
            [("content-type", "application/json")],
            json
        ).into_response()
    }
}