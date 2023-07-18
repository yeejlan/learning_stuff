use actix_web::web;

pub mod home_controller;
pub mod test_controller;
pub mod api;

pub fn service_config(cfg: &mut web::ServiceConfig) {
    home_controller::service_config(cfg);
    test_controller::service_config(cfg);
    api::user_controller::service_config(cfg);
}
