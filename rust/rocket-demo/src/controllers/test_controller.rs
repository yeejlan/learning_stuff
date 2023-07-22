use rocket::*;

use crate::{reply::Reply, exception::Exception, err_code, err_wrap};

pub fn build_routes(rocket: Rocket<Build>) -> Rocket<Build> {

    rocket.mount("/test", routes![
        action_err, 
        action_failed,
        action_err500,
        action_err_chain,
    ])
}

#[get("/err")]
async fn action_err() -> Result<Reply, Exception> {
    Err((401, "no permission"))?
}

#[get("/failed")]
async fn action_failed() -> Reply {
    Reply::failed("my testing error", err_code::OPERATION_NOT_ALLOWED)
}

#[get("/err500")]
async fn action_err500() -> Result<Reply, Exception> {
    let b = vec![0, 159, 146, 150];
    String::from_utf8(b)
        .map_err(|e| err_wrap!(e))?;

    Ok(Reply::success("success"))
}

#[get("/err-chain")]
async fn action_err_chain() -> Result<Reply, Exception> {
    let s = get_my_string()
        .await
        .map_err(|e| err_wrap!("My testing error!", e))?;
    
    Ok(Reply::success(s))
}

async fn _may_throw_error() -> Result<String, Exception> {
    let b = vec![0, 159, 146, 150];
    let s = String::from_utf8(b)
        .map_err(|e| err_wrap!("_may_throw_error failed!".to_owned(), e))?;

    Ok(s)
}

async fn get_my_string() -> Result<String, Exception> {
    let s = _may_throw_error()
        .await
        .map_err(|e| err_wrap!(err_code::OPERATION_FAILED, "get_my_string failed", e))?;
    Ok(s)
}