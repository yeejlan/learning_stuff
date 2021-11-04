FROM bitnami/php-fpm:8.0-prod

COPY docker/sources.list.buster /etc/apt/sources.list

RUN sed -i 's#date.timezone = UTC#date.timezone = Asia/Shanghai#g' /opt/bitnami/php/etc/php.ini

RUN sed -i 's#opcache.revalidate_freq = 60#opcache.revalidate_freq = 0#g' /opt/bitnami/php/etc/php.ini
RUN sed -i 's#opcache.memory_consumption = 128#opcache.memory_consumption = 256#g' /opt/bitnami/php/etc/php.ini
RUN sed -i 's#opcache.max_accelerated_files = 4000#opcache.max_accelerated_files = 20000#g' /opt/bitnami/php/etc/php.ini
RUN sed -i 's#;opcache.validate_timestamps=1#opcache.validate_timestamps=${PHP_OPCACHE_VALIDATE_TIMESTAMPS}#g' /opt/bitnami/php/etc/php.ini
RUN sed -i 's#opcache.interned_strings_buffer = 8#opcache.interned_strings_buffer = 16#g' /opt/bitnami/php/etc/php.ini

RUN install_packages supervisor nginx vim telnet curl net-tools inetutils-ping

COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer

COPY docker/supervisor/supervisord.conf /etc/supervisor/conf.d/
COPY docker/nginx/nginx.conf /etc/nginx/sites-enabled/default

ADD ./ /app

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]