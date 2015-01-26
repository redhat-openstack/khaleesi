#!/bin/bash -v

cat << EOF > /etc/yum.repos.d/rhel-internal.repo
[rhel7internal]
name=internal rhel repo
baseurl=http://{{ job.rh_download_server }}/released/RHEL-7/7.0/Workstation/x86_64/os/ 
enabled=1
gpgcheck=0

[rhel7internal-optional]
name=internal rhel repo
baseurl=http://{{ job.rh_download_server }}/released/RHEL-7/7.0/Workstation-optional/x86_64/os/ 
enabled=1
gpgcheck=0
EOF

yum -y install http://download.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm 2>&1

yum -y install httpd wordpress

sed -i "/Deny from All/d" /etc/httpd/conf.d/wordpress.conf
sed -i "s/Require local/Require all granted/" /etc/httpd/conf.d/wordpress.conf
sed -i s/database_name_here/$db_name/ /etc/wordpress/wp-config.php
sed -i s/username_here/$db_user/      /etc/wordpress/wp-config.php
sed -i s/password_here/$db_password/  /etc/wordpress/wp-config.php
sed -i s/localhost/$db_ipaddr/        /etc/wordpress/wp-config.php

setenforce 0 # Otherwise net traffic with DB is disabled

systemctl start httpd.service
