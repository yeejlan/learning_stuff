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
    Ok(())
}


pub fn add_to_inittab() -> () {
    pyo3::append_to_inittab!(spy_core);
}