
use std::collections::HashMap;

use axum::{Router, routing::post, extract::{Query, Path}, http::{HeaderMap, Method}};
use pyo3::{prelude::*, types::{PyString, PyTuple}};

use crate::{spy::{spy::SpyRequest, ope}, exception::Exception, err_wrap};

use super::spy::SpyResponse;

pub fn build_router(mut r: Router) -> Router {
    r = r.route("/p/:a", post(py_handler).get(py_handler));
    r = r.route("/p/:a/:b", post(py_handler).get(py_handler));
    r = r.route("/p/:a/:b/:c", post(py_handler).get(py_handler));
    r
}

async fn py_handler(
    method: Method,
    headers: HeaderMap,
    Path(path): Path<Vec<String>>, 
    Query(query): Query<HashMap<String, String>>,
    body: String) -> Result<SpyResponse, Exception>
{

    let path = path.join("/");

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
        controller: String::from(""),
        action: String::from(""),
    };

    let response = tokio::task::spawn_blocking(|| {

        Python::with_gil(|py| {
            PyModule::import(py, "operative")?
            .getattr("handle_request")?
            .call1((req,))?
            .extract::<SpyResponse>()
        })
        
    }).await
    .map_err(|e| err_wrap!("tokio join error", e) )?
    .map_err(|e| {

        Python::with_gil(|py| {

            if e.is_instance_of::<ope::UserException>(py) {
                let eo = e.to_object(py);
                let code = eo.getattr(py, "code").unwrap().extract::<i32>(py).unwrap();
                let message = eo.getattr(py, "message").unwrap().extract::<String>(py).unwrap();
                return Exception {
                    code,
                    message,
                    ..Default::default()
                }
            }

            let mut tr: String = "".into();
            if let Some(traceback) = e.traceback(py) {
                tr = format!("{}", traceback.format().unwrap_or(String::from("unknown py traceback.")));
            }

            let mut ex = err_wrap!("py_handler error", e);
            let mut c = ex.cause;

            for line in tr.lines() {
                c.push(line.to_string()); 
            }
            ex.cause = c;
            ex
        })
    });

    response
}

// fn handle_request_via_operative(req: SpyRequest) -> PyResult<&'static PyAny> {

//     Python::with_gil(|py| {
//         call_op1(py, "operative", "handle_request", (req,))
//     })
// }


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