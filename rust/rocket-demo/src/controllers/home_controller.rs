use rocket::*;

pub fn build_routes(rocket: Rocket<Build>) -> Rocket<Build> {
    rocket
        .mount("/", routes![index, hi])
}

#[get("/")]
fn index() -> &'static str {
    "this is /home/index page"
}

#[get("/hi")]
fn hi() -> &'static str {
    "say hi~"
}