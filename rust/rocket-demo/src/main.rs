use rocket_demo::controllers;

#[macro_use] extern crate rocket;


#[launch]
fn rocket() -> _ {

    controllers::build_routes()
    
}
