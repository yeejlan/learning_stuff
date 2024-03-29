
use actix_web::{App, HttpServer, web, http::header::{HeaderName, HeaderValue}, dev::Service, HttpMessage};

use hello::{controller, ext::{request_id_middleware::TracingLogger, request_id::RequestId}, app::{env_string, db::get_mysql_pool, AppContext}};

use tracing_log::LogTracer;
use tracing::subscriber::set_global_default;

fn init_subscriber() {

    let subscriber = tracing_subscriber::fmt()
    // Use a more compact, abbreviated log format
    .compact()
    // Don't display the event's target (module path)
    .with_target(false)
    // Build the subscriber
    .finish();    
    LogTracer::init().expect("Failed to set logger");
    set_global_default(subscriber).expect("Failed to set subscriber");
}



#[tokio::main]
async fn main() -> std::io::Result<()> {
    dotenvy::dotenv().expect(".evn file not found");

    init_subscriber();

    let ctx: AppContext = AppContext {
        db_default: get_mysql_pool("db_default").await,
    };

    HttpServer::new(move || {
        // custom `Json` extractor configuration
        let json_cfg = web::JsonConfig::default()
            // limit request payload size
            .limit(4096)
            // accept all content type
            .content_type(|_mime| true);        
        App::new()
            .app_data(web::Data::new(ctx.clone()))
            .wrap_fn(|req, srv| {
                let id = req.extensions()
                    .get::<RequestId>()
                    .copied().unwrap_or(RequestId::nil()).to_string();
                let fut = srv.call(req);

                async move {
                    let mut res = fut.await?;
                    res.headers_mut()
                        .insert(HeaderName::from_static("request-id"), HeaderValue::from_str(&id).unwrap());
                    Ok(res)
                }
            })
            .wrap(TracingLogger::default())
            .app_data(json_cfg)
            .configure(controller::service_config)
    })
    .bind(("0.0.0.0", 18080))?
    .run()
    .await
}