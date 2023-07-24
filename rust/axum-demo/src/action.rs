#[allow(unused_imports)]
use axum::{
    routing::{get, post, MethodRouter, on},
    Router,
};

/// Create router automatically
/// 
/// # Examples
/// 
/// ```
/// action!(post_get_home__say_hello) // POST, GET for URI: /home/say-hello and /say-hello
/// 
/// action!(get_home__index) // GET for URI: /home/index and /
/// 
/// action!(get_post_user__index) // GET, POST for URI: /user/index and /user
/// ```
/// 
/// # Name rule
///
/// ```
/// Start with "get_" or "post_" or "get_post_"
/// 
/// "__" for '/', "_" for "-"
/// 
/// "controller_name__action_name" for "/controller-name/action-name"
/// 
/// "home__action" for "/home/action" and "/action"
/// 
/// "controller__index" for "/controller/index" and "/controller"
/// ```
/// 
/// # If you got this error
/// 
/// ```
/// error[E0277]: the trait bound `fn() -> &'static str {get_home__index}: Handler<_, _, _>` is not satisfied
/// ```
/// 
/// It means your handler function is incorrect, for example
/// ```
///    fn get_home__index() -> &'static str {  //wrong, must be async function
///       "hello there"
///    }
/// ```
/// Should change to:
/// ```
///    async fn get_home__index() -> &'static str
///       "hello there"
///    }
/// ```
/// 
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
            let fn_name = crate::action::get_type($name);            
            panic!("Action[{}] must start with get or post, or both!", fn_name);
        }
        //convert "home__user_info" to "/home/user-info"
        let action_name = format!("/{}", name.replace("__", "/").replace("_", "-"));
        let mut router: Router = Router::new();
        let mut is_home_controller = false;
        let mut home_action = "";
        let mut is_index_action = false;
        let mut index_action = "";
        if(action_name.starts_with("/home/")) {
            is_home_controller = true;
            home_action = action_name.trim_start_matches("/home");
        }

        if(action_name.ends_with("/index")) {
            is_index_action = true;
            index_action = action_name.trim_end_matches("/index");
        }

        if(is_get) {
            router = router.route(&action_name, get($name));
            if(is_home_controller) {
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
            if(is_home_controller) {
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

pub fn get_type<T>(_: T) -> &'static str {
    std::any::type_name::<T>()
}

pub fn merge_routers(mut r: Router, routers: Vec<Router>) -> Router {
    for router in routers {
        r = r.merge(router);
    };
    r
}
