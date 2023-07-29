
use std::collections::HashMap;

use axum::{Router, routing::post, extract::{Query, Path}, http::{HeaderMap, Method}};
use pyo3::prelude::*;

use crate::spy::spy::SpyRequest;

pub fn build_router(mut r: Router) -> Router {
    r = r.route("/p/:path", post(py_handler).get(py_handler));
    r
}


async fn py_handler(
    method: Method,
    headers: HeaderMap,    
    Path(path): Path<String>, 
    Query(query): Query<HashMap<String, String>>,
    body: String) -> &'static str {

    let mut header_map = HashMap::new();
    for (key, value) in headers.iter() {
        header_map.insert(key.as_str().to_string(), 
            value.to_str().unwrap_or("").to_string());
    }

    let req = SpyRequest {
        method: method.to_string(),
        path,
        query,
        headers: header_map,
        body,
    };

    let e = handle_request_via_operative(req).await;
    dbg!(e);

    let _ = log("1123");
    "this is uri_handle_by_py"
}

pub async fn handle_request_via_operative(req: SpyRequest) -> PyResult<()> {

    Python::with_gil(|py| {
        let py_mod = PyModule::import(py, "operative")?;

        py_mod
            .getattr("handle_request")?
            .call1((req,))?;

        Ok(())
    })
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