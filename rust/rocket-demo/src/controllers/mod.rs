use rocket::*;

pub mod home_controller;
pub mod user_controller;

pub fn init_routes() -> Rocket<Build> {

    let mut r = rocket::build();

    r = home_controller::build_routes(r);
    r = user_controller::build_routes(r);
    
    r
}