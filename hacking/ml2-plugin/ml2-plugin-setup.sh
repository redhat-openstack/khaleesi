#! /usr/bin/env bash
set -e -u

SCRIPT_DIR=$(cd `dirname $0` && pwd)

ipv4_addr() {
    local iface=$1; shift
    ip addr show $iface |
        grep 'inet ' | awk '{ print $2 }' |
        cut -f1 -d/
}



ml2_plugin.install() {
    service neutron-server stop
    yum install -y openstack-neutron-ml2

}

ml2_plugin.neutron_config() {
    unlink /etc/neutron/plugin.ini || true
    ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini

    crudini --set /etc/neutron/neutron.conf DEFAULT core_plugin  \
            neutron.plugins.ml2.plugin.Ml2Plugin
    crudini --set /etc/neutron/neutron.conf DEFAULT service_plugins \
            neutron.services.l3_router.l3_router_plugin.L3RouterPlugin
}

ml2_plugin.config() {
    crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini \
        ml2 mechanism_drivers openvswitch
    crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini \
        ml2 tenant_network_types local,gre
    crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini \
        ml2_type_gre tunnel_id_ranges 1:1000

    crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini \
        database sql_connection \
        mysql://neutron:redhat@$(ipv4_addr eth0)/neutron_ml2
    crudini --set /etc/neutron/plugins/ml2/ml2_conf.ini \
        securitygroup firewall_driver \
        dummy_value
}

ml2_plugin.db_config() {
    mysql -e "drop database if exists neutron_ml2;"
    mysql -e "create database neutron_ml2 character set utf8;"
    mysql -e "grant all on neutron_ml2.* to 'neutron'@'%';"
    neutron-db-manage --config-file /usr/share/neutron/neutron-dist.conf \
        --config-file /etc/neutron/neutron.conf \
        --config-file /etc/neutron/plugin.ini upgrade head
}

main() {
    echo "Host ip: $(ipv4_addr eth0)"
    source ~/keystonerc_admin
    neutron agent-list | tee -a agent-list-old

    cp $SCRIPT_DIR/511471cc46b_agent_ext_model_supp.py \
        /usr/lib/python2.7/site-packages/neutron/db/migration/alembic_migrations/versions/511471cc46b_agent_ext_model_supp.py

    ml2_plugin.install

    ml2_plugin.neutron_config
    ml2_plugin.config
    ml2_plugin.db_config

    service neutron-server start
    neutron agent-list | tee -a agent-list-new
}

main "$@"
