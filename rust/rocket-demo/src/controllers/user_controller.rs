use rocket::*;

use crate::{models::user::{User, self}, reply::Reply};

pub fn build_routes(rocket: Rocket<Build>) -> Rocket<Build> {

    rocket.mount("/user", routes![
        index,
        hi,
        info,
        failed,
    ])
}

#[get("/index")]
fn index() -> &'static str {
    "this is /user/index page"
}

#[get("/hi")]
fn hi() -> &'static str {
    "this is user/info page"
}

#[get("/info")]
fn info() -> Reply  {
    let user = User {
        id: 123,
        name: "Chovy".into(),
        email: "Chovy@example.com".into(),
        password: "password here".into(),
        status: user::status::Active,
    };
    Reply::success(user)

}

#[get("/failed")]
fn failed() -> Reply  {
    Reply::failed("this request is not authorized", 401)
}