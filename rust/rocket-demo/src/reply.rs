use rocket::serde::json::Json;
use rocket::serde::json::serde_json::{Value, json};
use rocket::serde::Serialize;


pub type AppResponse = Json<JsonResponse>;

#[derive(Serialize)]
#[serde(crate = "rocket::serde")]
pub struct JsonResponse {
    code: i32,
    message: &'static str,
    reason: &'static str,
    data: Value,
}

pub fn success<T: Serialize>(resp: T) -> String {
    let data = json!({
        "code": 0,
        "message": "success".to_owned(),
        "reason": "success".to_owned(),
        "data": resp,
    });

    data.to_string()
}

// pub fn failed(message: &'static str, code: i32) -> Result<HttpResponse, Exception> {
//     let data = json!({
//         "code": code,
//         "message": message.to_owned(),
//         "reason": err_code::to_str(code).to_owned(),
//         "data": None::<i32>,
//     });    

//     ok_result(data)
// }

