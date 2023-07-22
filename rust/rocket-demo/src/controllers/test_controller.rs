use rocket::*;

use crate::{reply::Reply, exception::Exception, err_wrap, request_id::TracingSpan};

pub fn build_routes(rocket: Rocket<Build>) -> Rocket<Build> {

    rocket.mount("/test", routes![
        action_err, 
        action_err2,
        action_err3,
        action_failed,
        action_err500,
        action_err_chain,
    ])
}

#[get("/err")]
async fn action_err() -> Result<Reply, Exception> {
    Err((401, "not authorized!"))?
}

#[get("/err2")]
async fn action_err2() -> Result<Reply, Exception> {
    Err(("no permission", Reply::OPERATION_NOT_ALLOWED))?
}

#[get("/err3")]
async fn action_err3() -> Result<Reply, Exception> {
    Reply::result_error("error from replay::result_exception", Reply::BAD_RESULT)
}

#[get("/failed")]
async fn action_failed() -> Reply {
    Reply::failed("my testing error", Reply::OPERATION_FAILED )
}

#[get("/err500")]
async fn action_err500(span: TracingSpan) -> Result<Reply, Exception> {
    let entered = span.0.enter();
    info!("Hello World");
    drop(entered);
    info!("Hello again~~");
    let b = vec![0, 159, 146, 150];
    String::from_utf8(b)
        .map_err(|e| err_wrap!(e))?;

    Reply::result_success("success")
}

#[get("/err-chain")]
async fn action_err_chain() -> Result<Reply, Exception> {
    let s = get_my_string()
        .await
        .map_err(|e| err_wrap!("My testing error!", e))?;
    
    Reply::result_success(s)
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
        .map_err(|e| err_wrap!(Reply::OPERATION_FAILED, "get_my_string failed", e))?;
    Ok(s)
}