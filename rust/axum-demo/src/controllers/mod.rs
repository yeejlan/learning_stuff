
#[allow(unused_imports)]
use axum::{
    routing::{get, post, MethodRouter},
    Router,
};

#[macro_export]
macro_rules! action {
    ($name:path) => {{
        let action_fn = $name;
        let mut name = stringify!($name);
        let mut is_get = false;
        let mut is_post = false;
        let mut method = "post";
        if name.starts_with("get_") {
            is_get = true;
            name = name.trim_start_matches("get_");
            method = "get";
        }else if name.starts_with("post_") {
            is_post = true;
            name = name.trim_start_matches("post_");
        }
        if !is_get && !is_post {
            panic!("Action name need start with get or post!, got: {}", name);
        }
        //convert "home__user_info" to "/home/user-info"
        let action_name = format!("/{}", name.replace("33", "/").replace("_", "-"));

        Router::new().route(&action_name, method(action_fn))
    }};
}

pub fn merge_routers(mut r: Router, routers: Vec<Router>) -> Router {
    for router in routers {
        r = r.merge(router);
    };
    r
}

pub fn build_routers() -> Vec<Router> {
    vec![
        action!(get_home_say_hello),

    ]
    
}

async fn get_home_say_hello() -> &'static str {
    "hello from controllers~~"
}