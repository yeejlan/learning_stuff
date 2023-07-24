
use std::net::SocketAddr;

use axum::{
    routing::{get, post},
    Router,
};
use axum_demo::{controllers, app};
use tokio::signal;
use tower_http::{classify::ServerErrorsFailureClass, trace::TraceLayer, services::ServeDir};
use tracing::{info_span, Span};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};


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

    let mut router = Router::new();

    router = controllers::merge_routers(router, controllers::build_routers());
    router = router.nest_service("/public", ServeDir::new("public"));
    router = router.fallback(app::handler_404);

    // run it
    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    tracing::info!("listening on {}", addr);
    axum::Server::bind(&addr)
        .serve(router.into_make_service())
        .with_graceful_shutdown(app::shutdown_signal())
        .await
        .unwrap();  

}

