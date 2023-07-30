
use std::collections::HashMap;

use axum::{Router, routing::post, extract::{Query, Path}, http::{HeaderMap, Method}};
use pyo3::{prelude::*, types::{PyString, PyTuple}};

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
    body: String) -> &'static str 
{

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

        call_op1(py, "operative", "handle_request", (req,))?;

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

pub fn call_op0<N>(py: Python<'_>, py_mod: impl IntoPy<Py<PyString>>, 
    py_attr: impl IntoPy<Py<PyString>>) -> PyResult<&PyAny>
{
    PyModule::import(py, py_mod)?
        .getattr(py_attr)?
        .call0()
}

pub fn call_op1(py: Python<'_>, py_mod: impl IntoPy<Py<PyString>>, 
    py_attr: impl IntoPy<Py<PyString>>, py_args: impl IntoPy<Py<PyTuple>>) -> PyResult<&PyAny>
{
    PyModule::import(py, py_mod)?
        .getattr(py_attr)?
        .call1(py_args)
}