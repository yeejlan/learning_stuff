use axum::extract::FromRequest;


pub struct RequestId<T>(pub T);
