
#[allow(unused_imports)]
use axum::{
    routing::{get, post, MethodRouter},
    Router,
};

use crate::action;



pub fn merge_routers(mut r: Router, routers: Vec<Router>) -> Router {
    for router in routers {
        r = r.merge(router);
    };
    r
}

pub fn build_routers() -> Vec<Router> {
    vec![
        action!(post_get_home33say_hello),
        action!(get_home33index),
        action!(get_post_user33index),
        // action!(home33say_hello),
    ]
}

async fn _home33say_hello() -> &'static str {
    "this is /home/say-hello"
}

async fn post_get_home33say_hello() -> &'static str {
    "this is /home/say-hello"
}

async fn get_home33index() -> &'static str {
    "this is /home/index"
}

async fn get_post_user33index() -> &'static str {
    "this is /user/index"
}