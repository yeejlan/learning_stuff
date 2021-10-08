FROM bitnami/php-fpm:8.0-prod

COPY docker/sources.list.buster /etc/apt/sources.list

RUN sed -i 's#date.timezone = UTC#date.timezone = Asia/Shanghai#g' /opt/bitnami/php/etc/php.ini

RUN install_packages supervisor nginx

COPY docker/supervisor/supervisord.conf /etc/supervisor/conf.d/
COPY docker/nginx/nginx.conf /etc/nginx/sites-enabled/default

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]