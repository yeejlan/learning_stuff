use actix_web::{get, Responder, web};

use crate::ext::{reply, err_code, exception::Exception};

pub fn service_config(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/home")
        .service(response_code_action)
    );
}

#[get("/response-code")]
pub async fn response_code_action() -> Result<impl Responder, Exception> {
    reply::success(err_code::get_map())
}
