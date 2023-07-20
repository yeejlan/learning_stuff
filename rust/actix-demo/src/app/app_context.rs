use sqlx::mysql::MySqlPool;

#[derive(Clone, Debug)]
pub struct AppContext {
    pub db_default: MySqlPool,
}