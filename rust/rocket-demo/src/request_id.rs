use rocket::fairing::{Fairing, Info, Kind};
use rocket::http::Status;
use rocket::request::{FromRequest, Outcome};
use rocket::{Request, Data, Response};
use tracing::Span;
use uuid::Uuid;

pub struct RequestId(String);

#[derive(Clone)]
pub struct TracingSpan<T = Span>(pub T);
// Allows a route to access the span
#[rocket::async_trait]
impl<'r> FromRequest<'r> for TracingSpan {
    type Error = ();

    async fn from_request(request: &'r Request<'_>) -> Outcome<Self, ()> {
        match &*request.local_cache(|| TracingSpan::<Option<Span>>(None)) {
            TracingSpan(Some(span)) => Outcome::Success(TracingSpan(span.to_owned())),
            TracingSpan(None) => Outcome::Failure((Status::InternalServerError, ())),
        }
    }
}

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
        
        //let enter = span.enter();

        request.local_cache(|| TracingSpan::<Option<Span>>(Some(span)));
        

        request.local_cache(|| req_id);
    }

    async fn on_response<'r>(&self, request: &'r Request<'_>, response: &mut Response<'r>) {
        // if let Some(span) = request.local_cache(|| TracingSpan::<Option<Span>>(None)).0.to_owned() {
        //     let entered_span = span.entered();
        //     drop(entered_span);
        // }


        let req_id = request.local_cache(|| RequestId::new());
        response.set_raw_header("request-id", req_id.0.to_owned());
    }
}
