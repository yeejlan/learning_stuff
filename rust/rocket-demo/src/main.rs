use rocket_demo::{controllers, request_id::RequestId};

#[macro_use] extern crate rocket;


#[launch]
fn rocket() -> _ {
    dotenvy::dotenv().expect(".evn file not found");

    controllers::build_routes()
    .attach(RequestId::default())
}
