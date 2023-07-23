use axum::{
    routing::{get, post},
    Router,
};
use axum_demo::controllers;


fn build_routers() -> Vec<Router> {
    vec![
        Router::new().route("/hello", get(say_hello)),
        Router::new().route("/hi", post(say_hello).get(say_hello)),
    ]
}


async fn say_hello() -> &'static str {
    "hello there~"
}

#[tokio::main]
async fn main() {

    let mut app = Router::new().route("/", get(|| async { "Hello, World!" }));

    app = controllers::merge_routers(app, build_routers());
    app = controllers::merge_routers(app, controllers::build_routers());

    // run it with hyper on localhost:3000
    axum::Server::bind(&"0.0.0.0:13000".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}