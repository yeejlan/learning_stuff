pub mod handler;
pub mod rspy_core;

use pyo3::prelude::*;

pub fn init_py() -> PyResult<()> {
    let current_dir = std::env::current_dir().unwrap();
    let current_dir = current_dir.join("scripts");

    rspy_core::add_to_inittab();

    Python::with_gil(|py| {
        py.import("sys")?
        .getattr("path")?
        .call_method("append", (current_dir,), None)?;

        Ok(())
    })
}


pub fn call_py_add() -> PyResult<()> {

    Python::with_gil(|py| {
        let my_mod = PyModule::import(py, "handler")?;
        let total: i32 = my_mod
            .getattr("add")?
            .call1((1,2))?
            .extract()?;
        dbg!(&total);
    
        Ok(())
    })
}

pub fn call_rs_mod_in_py() -> PyResult<()> {

    Python::with_gil(|py| {
        let builtins = PyModule::import(py, "rspy_core")?;
        let total: i32 = builtins
            .getattr("add_one")?
            .call1((166,))?
            .extract()?;
        dbg!(&total);
        
        drop(builtins);
        Ok(())
    })
}