use rocket_demo::controllers;

#[macro_use] extern crate rocket;


#[launch]
fn rocket() -> _ {
    dotenvy::dotenv().expect(".evn file not found");

    controllers::build_routes()
}
