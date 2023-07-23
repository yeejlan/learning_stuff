
use axum::Router;

pub fn merge_routers(mut r: Router, routers: Vec<Router>) -> Router {
    for router in routers {
        r = r.merge(router);
    };
    r
}

