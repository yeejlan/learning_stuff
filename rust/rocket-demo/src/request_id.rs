use rocket::fairing::{Fairing, Info, Kind};
use rocket::{Request, Data, Response};
use tracing::Span;
use uuid::Uuid;

pub struct RequestId(String);
pub struct TracingSpan(Span);

impl RequestId {
    pub fn new() -> Self {
        RequestId(Uuid::new_v4().hyphenated().to_string())
    }

    pub fn from(req_id: &str) -> Self {
        RequestId(req_id.to_string())
    }

    pub fn default() -> Self {
        RequestId(String::from("0"))
    }
}

#[rocket::async_trait]
impl Fairing for RequestId {

    fn info(&self) -> Info {
        Info {
            name: "Add RequestId",
            kind: Kind::Request | Kind::Response
        }
    }

    //inherit RequestId from request header
    // async fn on_request(&self, request: &mut Request<'_>, _: &mut Data<'_>) {
    //     let id_may_exist: Option<&str> = request.headers().get_one("request-id");
    //     if let Some(id) = id_may_exist {
    //         let req_id = RequestId::from(id);
    //         request.local_cache(|| req_id);
    //     }else{
    //         request.local_cache(|| RequestId::new());
    //     }
    // }

    async fn on_request(&self, request: &mut Request<'_>, _: &mut Data<'_>) {

        let req_id = RequestId::new();

        let span = tracing::span!(
            tracing::Level::INFO,
            "request",
            request_id = %req_id.0,
        );
        
        let enter = span.entered();

        // request.local_cache(|| TracingSpan(span));
        

        request.local_cache(|| req_id);
    }

    async fn on_response<'r>(&self, request: &'r Request<'_>, response: &mut Response<'r>) {
        let req_id = request.local_cache(|| RequestId::new());
        response.set_raw_header("request-id", req_id.0.to_owned());
    }
}
