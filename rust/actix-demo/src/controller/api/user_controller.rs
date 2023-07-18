use actix_web::{get, Responder, web};

use crate::ext::{reply, exception::Exception};
use serde_json::json;

pub fn service_config(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/api/user")
        .service(action_info)
    );
}

#[get("/info")]
pub async fn action_info() -> Result<impl Responder, Exception> {
    reply::success(json!({
        "username" : "123",
        "gender" : "male",
    }))
}
