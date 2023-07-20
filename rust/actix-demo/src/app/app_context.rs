use actix_web::{dev::Payload, HttpMessage};
use actix_web::{FromRequest, HttpRequest, ResponseError};
use std::future::{ready, Ready};
use sqlx::mysql::MySqlPool;

#[derive(Clone, Debug)]
pub struct AppContext {
    pub db_default: MySqlPool,
}

impl FromRequest for AppContext {
    type Error = AppContextExtractionError;
    type Future = Ready<Result<Self, Self::Error>>;

    fn from_request(req: &HttpRequest, _: &mut Payload) -> Self::Future {
        ready(
            req.extensions()
                .get::<AppContext>()
                .cloned()
                .ok_or(AppContextExtractionError { _priv: () }),
        )
    }
}

#[derive(Debug)]
/// Error returned by the [`RequestId`] extractor when it fails to retrieve
/// the current request id from request-local storage.
///
/// It only happens if you try to extract the current request id without having
/// registered [`TracingLogger`] as a middleware for your application.
///
/// [`TracingLogger`]: crate::TracingLogger
pub struct AppContextExtractionError {
    // It turns out that a unit struct has a public constructor!
    // Therefore adding fields to it (either public or private) later on
    // is an API breaking change.
    // Therefore we are adding a dummy private field that the compiler is going
    // to optimise away to make sure users cannot construct this error
    // manually in their own code.
    _priv: (),
}

impl ResponseError for AppContextExtractionError {}

impl std::fmt::Display for AppContextExtractionError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Failed to retrieve app context from request-local storage."
        )
    }
}

impl std::error::Error for AppContextExtractionError {}