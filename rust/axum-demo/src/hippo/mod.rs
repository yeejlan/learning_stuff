
pub mod hippo;
pub mod hippo_handler;

use std::sync::Arc;

use once_cell::sync::Lazy;
use tokio::sync::Mutex;
use std::ops::Deref;

use self::hippo::HippoPool;

static HIPPO_POOL: Lazy<Arc<Mutex<HippoPool>>> = Lazy::new(|| {
    Arc::new(Mutex::new(HippoPool::new()))
});

pub async fn hippo_initialize() -> () {
    HIPPO_POOL.lock().await
        .set_max_exec_time(60)
        .set_worker_num(4)
        .set_php_executor("php".into())
        .set_worker_script("./hippo/worker.php".into())
        .build();
}

pub fn get_hippo_pool() -> Arc<Mutex<HippoPool>> {
    HIPPO_POOL.deref().clone()
}

