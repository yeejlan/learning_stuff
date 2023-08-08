
pub mod hippo;
pub mod worker;
pub mod hippo_handler;

use std::sync::Arc;

use once_cell::sync::OnceCell;

use self::hippo::{HippoPool, HippoConfig};

static HIPPO_CONFIG: OnceCell<Arc<HippoConfig>> = OnceCell::new();
static HIPPO_POOL: OnceCell<HippoPool> = OnceCell::new();


pub fn hippo_initialize() -> () {

    HIPPO_CONFIG.get_or_init(|| {
        let config = HippoConfig::new()
        .set_max_exec_time(30)
        .set_max_jobs_per_worker(500)
        .set_worker_num(1);

        Arc::new(config)
    });

    HIPPO_POOL.get_or_init(|| {
        HippoPool::new(get_hippo_config())
    });

}

pub fn get_hippo_pool() -> &'static HippoPool {
    HIPPO_POOL.get().unwrap().clone()
}

pub fn get_hippo_config() -> Arc<HippoConfig> {
    HIPPO_CONFIG.get().unwrap().clone()
}


