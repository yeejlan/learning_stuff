
use sqlx::mysql::{MySqlPoolOptions, MySqlPool};

pub async fn get_db_pool() -> MySqlPool {
    _db_pool().await
    .expect("can not connect to mysql")
}

async fn _db_pool() -> Result<MySqlPool, sqlx::Error> {
    let pool = MySqlPoolOptions::new()
        .connect("postgres://postgres:password@localhost/test").await?;
    Ok(pool)
}
