
use std::net::SocketAddr;

use axum::{
    routing::{get, post},
    Router,
};
use axum_demo::{controllers, app_fn};
use tokio::signal;
use tower_http::{classify::ServerErrorsFailureClass, trace::TraceLayer, services::ServeDir};
use tracing::{info_span, Span};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use tower_http::cors::CorsLayer;

#[tokio::main]
async fn main() {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| {
                "tower_http=debug,axum=debug".into()
            }),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let app = Router::new();

    let app = controllers::merge_routers(app, controllers::build_routers());
    let app = app.layer(app_fn::cors_layer());

    let app = app.nest_service("/public", ServeDir::new("public"));
    let app = app.fallback(app_fn::handler_404);
    let app = app.into_make_service();

    // run it
    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    tracing::info!("listening on {}", addr);
    axum::Server::bind(&addr)
        .serve(app)
        .with_graceful_shutdown(app_fn::shutdown_signal())
        .await
        .unwrap();  

}

