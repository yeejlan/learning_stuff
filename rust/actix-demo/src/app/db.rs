
use sqlx::mysql::{MySqlPoolOptions, MySqlPool};

use super::{env_u32, env_string};

pub async fn get_mysql_pool(db_name: &str) -> MySqlPool {
    _mysql_pool(db_name)
        .await
        .expect(&format! ("Can not connect to mysql [{}]", db_name))
}

async fn _mysql_pool(db_name: &str) -> Result<MySqlPool, sqlx::Error> {
    let key_dsn = format!("{}.dsn", db_name);
    let key_max_connections = format!("{}.connection.max", db_name);
    let key_min_connections = format!("{}.connection.min", db_name);
    let dsn = env_string(&key_dsn);
    let max_connections = env_u32(&key_max_connections);
    let min_connections = env_u32(&key_min_connections);

    let pool = MySqlPoolOptions::new()
        .max_connections(max_connections)
        .min_connections(min_connections)
        .connect(&dsn)
        .await?;
    Ok(pool)
}
