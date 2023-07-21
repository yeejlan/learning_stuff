use rocket_demo::controllers;

#[macro_use] extern crate rocket;


#[launch]
fn rocket() -> _ {
    let rocket = controllers::init_routes();
    rocket
}
