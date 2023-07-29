pub mod spy_handler;
pub mod spy;

use pyo3::prelude::*;

pub fn spy_initialize() -> PyResult<()> {
    let current_dir = std::env::current_dir().unwrap();
    let current_dir = current_dir.join("scripts");

    spy::add_to_inittab();

    Python::with_gil(|py| {
        py.import("sys")?
        .getattr("path")?
        .call_method("append", (current_dir,), None)?;

        Ok(())
    })
}
