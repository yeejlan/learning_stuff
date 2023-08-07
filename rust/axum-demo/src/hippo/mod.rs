
pub mod hippo;
pub mod worker;
pub mod hippo_handler;

use std::sync::Arc;

use once_cell::sync::Lazy;
use tokio::sync::RwLock;
use std::ops::Deref;

use self::hippo::{HippoPool, HippoConfig};

static HIPPO_POOL: Lazy<Arc<RwLock<HippoPool>>> = Lazy::new(|| {

    let pool = HippoPool::new();
    Arc::new(RwLock::new(pool))
});


pub async fn hippo_initialize() -> () {

    //does not work!!!
    let config = HippoConfig::new()
        .set_max_exec_time(30)
        .set_max_jobs_per_worker(500)
        .set_worker_num(8);

    get_hippo_pool().write().await
        .init_worker_pool(config);
}

pub fn get_hippo_pool() -> Arc<RwLock<HippoPool>> {
    HIPPO_POOL.deref().clone()
}
