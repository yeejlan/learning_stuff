pub mod db;
pub mod app_context;

use std::env;

pub use app_context::AppContext;


pub fn env_string(key: &str) -> String {
    match env::var(key) {
        Ok(val) => val,
        Err(_e) => String::from(""),
    }
}

pub fn env_u32(key: &str) -> u32 {
    match env::var(key) {
        Ok(val) => val.parse::<u32>().unwrap_or(0),
        Err(_e) => 0,
    }
}