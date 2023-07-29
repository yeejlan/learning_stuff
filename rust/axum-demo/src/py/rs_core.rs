use pyo3::prelude::*;

#[pyfunction]
fn add_one(x: i64) -> i64 {
    println!("x={}", x);
    x + 1
}

#[pymodule]
fn rs_core(_py: Python<'_>, rs_core_module: &PyModule) -> PyResult<()> {
    rs_core_module.add_function(wrap_pyfunction!(add_one, rs_core_module)?)?;
    Ok(())
}


pub fn add_to_inittab() -> () {
    pyo3::append_to_inittab!(rs_core);
}