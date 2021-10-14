# Flyway

https://flywaydb.org/

### Quick start

```bash
docker-compose up
```

Or

```bash
docker build -t flyway-mysql:v1 . 

docker run -it -v [path_to_conf]:/flyway/conf -v [path_to_sql]:/flyway/sql flyway-mysql:v1 migrate
```

### Docker

https://github.com/flyway/flyway-docker