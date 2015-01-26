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

yum -y remove mariadb-libs mariadb mariadb-server
yum -y install mariadb mariadb-server
touch /var/log/mariadb/mariadb.log
chown mysql.mysql /var/log/mariadb/mariadb.log
systemctl start mariadb.service

# Setup MySQL root password and create a user
mysqladmin -u root password $db_rootpassword
cat << EOF | mysql -u root --password=$db_rootpassword
CREATE DATABASE $db_name;
GRANT ALL PRIVILEGES ON $db_name.* TO '$db_user'@'%'
IDENTIFIED BY '$db_password';
FLUSH PRIVILEGES;
EXIT
EOF
