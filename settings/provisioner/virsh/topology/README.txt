This is a placeholder for the new provisioner to hold the topology files
in the form of:

provisioner:
    hosts:
        # Dict of hosts to use for virt deployment (currently only 1 supported)
        host1:
            name: virthost
            ssh_host: "{{ MANDATORY_FIELD }}"
            ssh_user: root
            ssh_key_file: ~/.ssh/id_rsa
            groups:
                - virthost

    nodes:
        # Dict of nodes
        example:
            name: undercloud
            cpu: !lookup provisioner.image.cpu
            memory: !lookup provisioner.image.memory
            os:
                type: linux
                variant: !lookup provisioner.image.os.variant
            disk:
                size: !lookup provisioner.image.disk.size
                path: /var/lib/libvirt/images
            groups:
                - undercloud
                - openstack_nodes


