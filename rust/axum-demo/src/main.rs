
use axum::{Router, http::Request, extract::MatchedPath,};
use axum_demo::{controllers, app_fn, spy};
use tower_http::{trace::TraceLayer, services::ServeDir, request_id::RequestId};
use tracing::{info_span, Span};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[tokio::main]
async fn main() {
    dotenvy::dotenv().expect(".evn file not found");

    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| {
                "tower_http=debug,axum=debug".into()
            }),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let _ = spy::spy_initialize();

    let app = Router::new();

    let app = spy::spy_handler::build_router(app);
    
    let app = controllers::merge_routers(app, controllers::build_routers());
    let app = app.layer(app_fn::cors_layer());

    let app = app.layer(app_fn::propagate_request_id_layer());
    let app = app.layer(
        TraceLayer::new_for_http()
            .make_span_with(|request: &Request<_>| {
                // Log the matched route's path (with placeholders not filled in).
                // Use request.uri() or OriginalUri if you want the real path.
                let matched_path = request
                    .extensions()
                    .get::<MatchedPath>()
                    .map(MatchedPath::as_str);

                info_span!(
                    "http_request",
                    method = ?request.method(),
                    matched_path,
                    request_id = tracing::field::Empty,
                )
            })
            .on_request(|request: &Request<_>, span: &Span| {
                let req_id = &request.extensions()
                    .get::<RequestId>()
                    .map(|r| r.header_value().to_str().unwrap())
                    .unwrap();

                span.record("request_id", req_id);
            })
    );
    let app = app.layer(app_fn::set_request_id_layer());


    let app = app.nest_service("/public", ServeDir::new("public"));
    let app = app.fallback(app_fn::handler_404);
    let app = app.into_make_service();

    // run it
    let addr = "0.0.0.0:8080";
    tracing::info!("listening on {}", addr);
    axum::Server::bind(&addr.parse().unwrap())
    .serve(app)
    .with_graceful_shutdown(app_fn::shutdown_signal())
    .await
    .unwrap();

}

