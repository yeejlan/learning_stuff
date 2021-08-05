FROM yiisoftware/yii2-php:7.4-apache

# mirrors.aliyun.com
RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN sed -i s@/security.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list

# Change document root for Apache
RUN sed -i -e 's|/app/web|/app/public|g' /etc/apache2/sites-available/000-default.conf