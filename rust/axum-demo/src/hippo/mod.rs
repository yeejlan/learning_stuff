
pub mod hippo;
pub mod hippo_handler;

use std::sync::{Arc, Mutex};

use once_cell::sync::Lazy;
use std::ops::Deref;

use self::hippo::HippoManager;

static HIPPO_MANAGER: Lazy<Arc<Mutex<HippoManager>>> = Lazy::new(|| {
    Arc::new(Mutex::new(HippoManager::new()))
});

pub fn hippo_initialize() -> () {
    HIPPO_MANAGER.lock().unwrap()
        .set_max_exec_time(60)
        .set_worker_num(4)
        .set_php_executor("php".into())
        .set_worker_script("./hippo/worker.php".into())
        .build();
}

pub fn get_hippo_manager() -> Arc<Mutex<HippoManager>> {
    HIPPO_MANAGER.deref().clone()
}

