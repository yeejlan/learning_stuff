use std::collections::HashMap;

use axum::{response::{Response, IntoResponse}, http::{StatusCode, HeaderMap}};
use pyo3::prelude::*;

use crate::reply::Reply;

#[pyfunction]
fn tracing_debug(msg: &str) -> () {
    tracing::log::debug!("{}", msg);
}

#[pyfunction]
fn tracing_info(msg: &str) -> () {
    tracing::log::info!("{}", msg);
}

#[pyfunction]
fn tracing_warn(msg: &str) -> () {
    tracing::log::warn!("{}", msg);
}

#[pyfunction]
fn tracing_error(msg: &str) -> () {
    tracing::log::error!("{}", msg);
}

#[pyfunction]
fn code_to_reason(code: i32) -> &'static str {
    Reply::code_to_str(code)
}

#[pymodule]
fn spy(_py: Python<'_>, py_module: &PyModule) -> PyResult<()> {
    py_module.add_function(wrap_pyfunction!(tracing_debug, py_module)?)?;
    py_module.add_function(wrap_pyfunction!(tracing_info, py_module)?)?;
    py_module.add_function(wrap_pyfunction!(tracing_warn, py_module)?)?;
    py_module.add_function(wrap_pyfunction!(tracing_error, py_module)?)?;
    py_module.add_function(wrap_pyfunction!(code_to_reason, py_module)?)?;
    py_module.add_class::<SpyRequest>()?;
    py_module.add_class::<SpyResponse>()?;
    Ok(())
}


pub fn add_to_inittab() -> () {
    pyo3::append_to_inittab!(spy);
}

#[pyclass]
#[derive(FromPyObject, Debug)]
pub struct SpyRequest {
    #[pyo3(get)]
    pub method: String,
    #[pyo3(get)]
    pub path: String,
    #[pyo3(get)]
    pub query: HashMap<String, String>,
    #[pyo3(get)]
    pub headers: HashMap<String, String>,
    #[pyo3(get)]
    pub body: String,
}

#[pymethods]
impl SpyRequest {
    fn __repr__(&self) -> String {
        format!("SpyRequest({})", self.path)
    }

    fn __str__(&self) -> String {
        format!("{:#?}", self)
    }

    fn request_id(&self) -> String {
        self.headers.get("request-id")
        .unwrap().to_owned()
    }
}

#[pyclass]
#[derive(FromPyObject, Debug)]
pub struct SpyResponse {
    #[pyo3(get, set)]
    pub status_code: u16,
    #[pyo3(get, set)]
    pub headers: HashMap<String, String>,
    #[pyo3(get, set)]
    pub content: String,
}

#[pymethods]
impl SpyResponse {
    fn __repr__(&self) -> String {
        format!("SpyResponse({} {})", self.status_code, self.content)
    }
    fn __str__(&self) -> String {
        format!("{:#?}", self)
    }

    #[new]
    fn new() -> Self {
        Self {
            status_code: 200,
            headers: HashMap::new(),
            content: String::from(""),
        }
    }
}

impl IntoResponse for SpyResponse {
    fn into_response(self) -> Response {

        let headers: HeaderMap = (&self.headers).try_into().unwrap_or(HeaderMap::new());

        let status_code = StatusCode::from_u16(self.status_code).unwrap();
        (
            status_code,
            headers,
            self.content
        ).into_response()
    }
}