use rocket_demo::{controllers, request_id::RequestId};

#[macro_use] extern crate rocket;

use tracing_log::LogTracer;
use tracing::subscriber::set_global_default;

fn init_subscriber() {
    use tracing_subscriber::prelude::*;

    let subscriber = tracing_subscriber::fmt()
    .compact()
    .with_target(false)
    // Build the subscriber
    .finish();


    LogTracer::init().expect("Failed to set logger");
    set_global_default(subscriber).expect("Failed to set subscriber");
}



#[launch]
fn rocket() -> _ {
    dotenvy::dotenv().expect(".evn file not found");

    init_subscriber();

    controllers::build_routes()
    .attach(RequestId::default())

}
