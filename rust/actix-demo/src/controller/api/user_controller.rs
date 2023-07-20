use actix_web::{get, Responder, web};

use crate::{ext::exception::Exception, model::user_model::{self, UserModel}, app::AppContext};

use serde::{Serialize, Deserialize};

pub fn service_config(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/api/user")
        .service(action_info)
    );
}

#[derive(Serialize, Deserialize, Debug)]
pub struct InfoParams {
    user_id: i64,
}
#[get("/info")]
pub async fn action_info(ctx: web::Data<AppContext>, params: web::Json<InfoParams>) -> Result<impl Responder, Exception> {

    let row = user_model::get_user_info(ctx, params.user_id)
    .await?;
    dbg!(row);
    Ok("OK")
}
