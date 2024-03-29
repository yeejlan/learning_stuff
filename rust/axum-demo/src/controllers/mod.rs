pub mod test_controller;

#[allow(unused_imports)]
use axum::{
    routing::{get, post, MethodRouter},
    Router,
};

use crate::{action, reply::{self, Reply}};



pub fn merge_routers(mut r: Router, routers: Vec<Router>) -> Router {
    for router in routers {
        r = r.merge(router);
    };
    r
}

pub fn build_routers() -> Vec<Router> {
    vec![
        action!(post_get_home__say_hello),
        action!(get_home__index),
        action!(get_post_user__index),
        action!(get_home__hi),
        action!(get_home__err),
        action!(get_home__sleep),
        action!(get_home__sleep2),
        // action!(home__say_hello),
    ]
}

// #[axum::debug_handler]
async fn get_home__hi() -> reply::Result<Reply> {
    Reply::result_success("this is hello message for testing")
}

async fn get_home__err() -> reply::Result<Reply> {
    let s = "this is error message".to_string();
    Reply::result_failed(&s, Reply::BAD_RESULT)
}

async fn get_home__sleep() -> Reply {
    tokio::time::sleep(std::time::Duration::from_millis(10)).await;
    Reply::success("sleep 10ms using tokio::time::sleep")
}

async fn get_home__sleep2() -> Reply {
    tokio::task::spawn_blocking(|| {

        std::thread::sleep(std::time::Duration::from_millis(10)); 
        Reply::success("sleep 10ms using std::thread::sleep")
        
    }).await.unwrap()

}

async fn _home__say_hello() -> &'static str {
    "this is /home/say-hello"
}

async fn post_get_home__say_hello() -> &'static str {
    "this is /home/say-hello"
}

async fn get_home__index() -> &'static str {
    tracing::info!("hi~");
    "this is /home/index"
}

async fn get_post_user__index() -> &'static str {
    "this is /user/index"
}

