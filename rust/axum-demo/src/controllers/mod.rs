
#[allow(unused_imports)]
use axum::{
    routing::{get, post, MethodRouter},
    Router,
};

#[macro_export]
macro_rules! action {
    ($name:path) => {{
        let mut name = stringify!($name);
        let mut is_get = false;
        let mut is_post = false;
        if name.starts_with("get_") {
            is_get = true;
            name = name.trim_start_matches("get_");
        }
        if name.starts_with("post_") {
            is_post = true;
            name = name.trim_start_matches("post_");
        }
        if name.starts_with("get_") { // check it again, since post_get_ works too
            is_get = true;
            name = name.trim_start_matches("get_");
        }        
        if !is_get && !is_post {
            panic!("Action name must start with get or post, or both!, got: {}", name);
        }
        //convert "home__user_info" to "/home/user-info"
        let action_name = format!("/{}", name.replace("33", "/").replace("_", "-"));
        let mut router: Router = Router::new();
        let mut is_home_controll = false;
        let mut home_action = "";
        let mut is_index_action = false;
        let mut index_action = "";
        if(action_name.starts_with("/home/")) {
            is_home_controll = true;
            home_action = action_name.trim_start_matches("/home");
        }

        if(action_name.ends_with("/index")) {
            is_index_action = true;
            index_action = action_name.trim_end_matches("/index");
        }

        if(is_get) {
            router = router.route(&action_name, get($name));
            if(is_home_controll) {
                router = router.route(home_action, get($name));
            }
            if(is_index_action) {
                router = router.route(index_action, get($name));
            }
            if(action_name == "/home/index") {
                router = router.route("/", get($name));
            }            
        }
        if(is_post) {
            router = router.route(&action_name, post($name));
            if(is_home_controll) {
                router = router.route(home_action, post($name));
            }
            if(is_index_action) {
                router = router.route(index_action, post($name));
            }
            if(action_name == "/home/index") {
                router = router.route("/", post($name));
            }            
        }

        router
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
        action!(post_get_home33say_hello),
        action!(get_home33index),
        action!(get_post_user33index),
    ]
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