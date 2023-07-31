pub mod spy_handler;
pub mod spy;

use pyo3::prelude::*;

use crate::reply::Reply;

pub fn spy_initialize() -> () {
    let current_dir = std::env::current_dir().unwrap();
    let current_dir = current_dir.join("operative");

    Reply::code_to_str(Reply::SUCCESS); //make sure map initialized

    spy::add_to_inittab();

    Python::with_gil(|py| {
        py.import("sys").unwrap()
        .getattr("path").unwrap()
        .call_method("append", (current_dir,), None).unwrap();

        py.import("operative").unwrap();
    })
}

pub mod ope {
    pyo3::import_exception!(ope, UserException);
    pyo3::import_exception!(ope, ModelException);
    pyo3::import_exception!(ope, ServiceException);
    pyo3::import_exception!(ope, FluxException);
}