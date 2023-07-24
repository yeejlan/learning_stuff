use axum::http::Request;
use tower_http::request_id::MakeRequestId;
use uuid::Uuid;


#[derive(Clone)]
pub struct RequestId(pub String);

impl RequestId {
    pub fn new() -> Self {
        Self(Uuid::new_v4().hyphenated().to_string())
    }

    pub fn from(req_id: &str) -> Self {
        Self(req_id.to_string())
    }

    pub fn default() -> Self {
        Self(Uuid::nil().hyphenated().to_string())
    }
}

