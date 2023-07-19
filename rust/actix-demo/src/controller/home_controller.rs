use actix_web::{get, Responder, web};

use crate::ext::{reply, err_code, exception::Exception};

pub fn service_config(cfg: &mut web::ServiceConfig) {

    cfg.service(action_health_check)
        .service(action_response_code);
}

#[get("/response-code")]
pub async fn action_response_code() -> Result<impl Responder, Exception> {
    reply::success(err_code::get_map())
}

#[get("/health-check")]
async fn action_health_check() -> impl Responder {
    "hi~"
}