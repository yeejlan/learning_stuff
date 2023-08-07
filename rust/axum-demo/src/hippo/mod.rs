
pub mod hippo;
pub mod hippo_handler;

use std::sync::Arc;

use once_cell::sync::Lazy;
use tokio::sync::RwLock;
use std::ops::Deref;

use self::hippo::HippoPool;

static HIPPO_POOL: Lazy<Arc<RwLock<HippoPool>>> = Lazy::new(|| {
    let pool = HippoPool::new(8);
    Arc::new(RwLock::new(pool))
});

pub async fn hippo_initialize() -> () {
    get_hippo_pool().write().await
        .set_php_executor("php".into())
        .set_worker_script("./hippo/worker.php".into())
        .set_max_exec_time(60)
        .build();

}

pub fn get_hippo_pool() -> Arc<RwLock<HippoPool>> {
    HIPPO_POOL.deref().clone()
}

