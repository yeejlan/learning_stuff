use axum::{Router, routing::post};
use pyo3::prelude::*;

pub fn build_router(mut r: Router) -> Router {
    r = r.route("/p/:path", post(uri_endwith_py_handler).get(uri_endwith_py_handler));
    r
}


async fn uri_endwith_py_handler() -> &'static str {
    let _ = log("1123");
    "this is uri_endwith_py_handler"
}

fn log(msg: &str) -> PyResult<()> {

    Python::with_gil(|py| {
        let builtins = PyModule::import(py, "spy_core")?;
        builtins
            .getattr("log")?
            .call1((msg,))?;

        Ok(())
    })
}