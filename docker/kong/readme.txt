https://blog.csdn.net/a12345678n/article/details/106520180

1. 创建kong-net网络
docker network create kong-net

2. 启动PostgreSQL容器
docker run -d --name kong-database --network=kong-net -p 5432:5432 -e "POSTGRES_USER=kong" -e "POSTGRES_DB=kong" -e "POSTGRES_PASSWORD=kong" postgres:9.6

3. 运行临时Kong容器迁移数据库

docker run --rm --network=kong-net -e "KONG_DATABASE=postgres" -e "KONG_PG_HOST=kong-database" -e "KONG_PG_PASSWORD=kong" -e "KONG_CASSANDRA_CONTACT_POINTS=kong-database" kong:latest kong migrations bootstrap

4. 启动Kong容器
docker run -d --name kong --network=kong-net -e "KONG_DATABASE=postgres" -e "KONG_PG_HOST=kong-database" -e "KONG_PG_PASSWORD=kong" -e "KONG_CASSANDRA_CONTACT_POINTS=kong-database" -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" -e "KONG_PROXY_ERROR_LOG=/dev/stderr" -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" -e "KONG_ADMIN_LISTEN=0.0.0.0:8001, 0.0.0.0:8444 ssl" -p 8000:8000 -p 8443:8443 -p 8001:8001 -p 8444:8444 kong:latest

5. 验证kong

curl -i -X GET --url http://127.0.0.1:8001/services
 
6. 初始化konga

docker run --name konga --rm --network=kong-net pantsel/konga -c prepare -a postgres -u postgresql://kong:kong@kong-database:5432/kong

7. 启动konga

docker run -p 1337:1337 -d --network=kong-net -e "DB_ADAPTER=postgres" -e "DB_HOST=kong-database" -e "DB_USER=kong" -e "DB_PASSWORD=kong" -e "DB_DATABASE=kong" -e "KONGA_HOOK_TIMEOUT=120000" -e "DB_PG_SCHEMA=public" -e "NODE_ENV=production" --name konga pantsel/konga

