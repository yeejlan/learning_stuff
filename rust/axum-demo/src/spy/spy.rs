use std::collections::HashMap;

use pyo3::{prelude::*, types::PyString};

#[pyfunction]
fn tracing_debug(msg: &str) -> () {
    tracing::debug!(msg);
}

#[pyfunction]
fn tracing_info(msg: &str) -> () {
    tracing::info!(msg);
}

#[pyfunction]
fn tracing_warn(msg: &str) -> () {
    tracing::warn!(msg)
}

#[pyfunction]
fn tracing_error(msg: &str) -> () {
    tracing::error!(msg)
}

#[pymodule]
fn spy(_py: Python<'_>, py_module: &PyModule) -> PyResult<()> {
    py_module.add_function(wrap_pyfunction!(tracing_debug, py_module)?)?;
    py_module.add_function(wrap_pyfunction!(tracing_info, py_module)?)?;
    py_module.add_function(wrap_pyfunction!(tracing_warn, py_module)?)?;
    py_module.add_function(wrap_pyfunction!(tracing_error, py_module)?)?;
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
    pub method: String,
    pub path: String,
    pub query: HashMap<String, String>,
    pub headers: HashMap<String, String>,
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
    pub status_code: u16,
    pub headers: HashMap<String, String>,
    pub content: Vec<u8>,
}

#[pymethods]
impl SpyResponse {
    fn __repr__(&self) -> String {
        format!("SpyResponse({})", self.status_code)
    }
    fn __str__(&self) -> String {
        format!("{:#?}", self)
    }
}
