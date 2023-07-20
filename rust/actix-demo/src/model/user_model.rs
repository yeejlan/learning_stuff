use actix_web::web;
use sqlx::{types::chrono::{Utc, DateTime}};

use crate::app::AppContext;
#[derive(Debug)]
pub struct UserModel {
    pub id: i64,
    pub name: String,
    pub email: Option<String>,
    pub password: String,
    pub status: Option<i32>,
    pub created_at: Option<DateTime::<Utc>>,
    pub updated_at: Option<DateTime::<Utc>>,
}

pub async fn get_user_info(ctx: web::Data<AppContext>, user_id: i64) -> Result<UserModel, sqlx::Error> {

    sqlx::query_as!(UserModel,
        r#"
select * from users where id = ?
        "#,
        user_id
    )
    .fetch_one(&ctx.db_default)
    .await
}

pub mod status {
    use cached::proc_macro::once;
    use std::collections::BTreeMap;

    use crate::ext::exception::Exception;


    pub const NORMAL: i32 = 1;
    pub const ACTIVE: i32 = 2;
    pub const FROZEN: i32 = 3;
    pub const CLOSED: i32 = 4;

    #[once]
    pub fn get_map() -> BTreeMap<i32, String> {
        BTreeMap::from([
            (NORMAL, String::from("normal")),
            (ACTIVE, String::from("active")),
            (FROZEN, String::from("frozen")),
            (CLOSED, String::from("closed")),
        ])
    }

    #[once]
    pub fn get_map_reversed() -> BTreeMap<String, i32> {
        let mut m: BTreeMap<String, i32> = BTreeMap::new();
        for v in get_map() {
            m.insert(v.1.to_owned(), v.0);
        };
        m
    }

    pub fn from_str(value: &str) -> Result<i32, Exception> {
        let m = get_map_reversed();
        m.get(value)
            .copied()
            .ok_or_else(|| Exception::from(format!("status not found: {}", value)) )
    }

    pub fn to_str(value: i32)-> Result<String, Exception> {
        let m = get_map();
        m.get(&value)
            .cloned()
            .ok_or_else(|| Exception::from(format!("status not found: {}", value)) )
            
    }
}

