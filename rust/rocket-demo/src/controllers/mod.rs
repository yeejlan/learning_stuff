use rocket::*;

pub mod home_controller;
pub mod user_controller;
pub mod test_controller;

pub fn build_routes() -> Rocket<Build> {

    let mut r = rocket::build();

    r = home_controller::build_routes(r);
    r = user_controller::build_routes(r);
    r = test_controller::build_routes(r);
    
    r
}