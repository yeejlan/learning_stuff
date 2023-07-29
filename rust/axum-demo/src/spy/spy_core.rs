use std::collections::HashMap;

use pyo3::prelude::*;

#[pyfunction]
fn add_one(x: i64) -> i64 {
    println!("x={}", x);
    x + 1
}

#[pyfunction]
fn log(msg: &str) -> () {
    tracing::info!(msg);
}

#[pymodule]
fn spy_core(_py: Python<'_>, py_module: &PyModule) -> PyResult<()> {
    py_module.add_function(wrap_pyfunction!(add_one, py_module)?)?;
    py_module.add_function(wrap_pyfunction!(log, py_module)?)?;
    py_module.add_class::<SpyRequest>()?;
    py_module.add_class::<SpyResponse>()?;
    Ok(())
}


pub fn add_to_inittab() -> () {
    pyo3::append_to_inittab!(spy_core);
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
