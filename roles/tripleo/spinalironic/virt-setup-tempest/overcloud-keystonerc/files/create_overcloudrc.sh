source instack.answers
source tripleo-overcloud-passwords
export OVERCLOUD_IP=$(nova list | grep controller0.*ctlplane | sed  -e "s/.*=\\([0-9.]*\\).*/\1/")
export TE_DATAFILE=/home/stack/instackenv.json
sudo cp /etc/tripleo/overcloudrc_template .

source overcloudrc_template

cat <<EOF > overcloudrc
export NOVA_VERSION=1.1
export OS_PASSWORD=$OS_PASSWORD
export OS_AUTH_URL=$OS_AUTH_URL
export OS_USERNAME=admin
export OS_TENANT_NAME=admin
export COMPUTE_API_VERSION=1.1
export OS_NO_CACHE=True
export OS_CLOUDNAME=overcloud
EOF
