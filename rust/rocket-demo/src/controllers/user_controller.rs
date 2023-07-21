use rocket::*;

pub fn build_routes(rocket: Rocket<Build>) -> Rocket<Build> {
    rocket
        .mount("/user", routes![index, hi])
}

#[get("/index")]
fn index() -> &'static str {
    "this is /user/index page"
}

#[get("/info")]
fn hi() -> &'static str {
    "this is user/info page"
}