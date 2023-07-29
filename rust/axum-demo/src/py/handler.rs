use axum::{Router, routing::post};

pub fn build_router(mut r: Router) -> Router {
    r = r.route("/p/:path", post(uri_endwith_py_handler).get(uri_endwith_py_handler));
    r
}


async fn uri_endwith_py_handler() -> &'static str {
    "this is uri_endwith_py_handler"
}