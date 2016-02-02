Khaleesi Best Practices Guide
=============================

The purpose of this guide is to lay out the coding standards and best practices to be applied when
working with Khaleesi. These best practices are specific to Khlaeesi but should be in line with
general `Ansible guidelines <https://github.com/ansible/ansible/blob/devel/docsite/rst/playbooks_best_practices.rst>`_.

Each section includes:
 * A 'Rule' which states the best practice to apply
 * Explanations and notable exceptions
 * Examples of code applying the rule and, if applicable, examples of where the exceptions would hold

General Best Practices
----------------------

**Rule: Whitespace and indentation** - Use 4 spaces.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ensure that you use 4 spaces, not tabs, to separate each level of indentation.

Examples::

    # BEST_PRACTICES_APPLIED
    - name: set plan values for plan based ceph deployments
      shell: >
          source {{ instack_user_home }}/stackrc;
          openstack management plan set {{ overcloud_uuid }}
              -P Controller-1::CinderEnableIscsiBackend=false;
      when: installer.deploy.type == 'plan'


**Rule: Parameter Format** - Use the YAML dictionary format when 3 or more parameters are being passed.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When several parameters are being passed in a module, it is hard to see exactly what value each
parameter is getting. It is preferable to use the Ansible YAML syntax to pass in parameters so
that it is clear what values are being passed for each parameter.

Examples::

    # Step with all arguments passed in one line
    - name: create .ssh dir
      file: path=/home/{{ provisioner.remote_user }}/.ssh mode=0700 owner=stack group=stack state=directory

    # BEST_PRACTICE_APPLIED
    - name: create .ssh dir
      file:
          path: /home/{{ provisioner.remote_user }}/.ssh
          mode: 0700
          owner: stack
          group: stack
          state: directory


**Rule: Line Length** - Keep text under 100 characters per line.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For ease of readability, keep text to a uniform length of 100 characters or less. Some modules
are known to have issues with multi-line formatting and should be commented on if it is an issue
within your change.

Examples::

    # BEST_PRACTICE_APPLIED
    - name: set plan values for plan based ceph deployments
      shell: >
          source {{ instack_user_home }}/stackrc;
          source {{ instack_user_home }}/deploy-nodesrc;
          openstack management plan set {{ overcloud_uuid }}
              -P Controller-1::CinderEnableIscsiBackend=false
              -P Controller-1::CinderEnableRbdBackend=true
              -P Controller-1::GlanceBackend=rbd
              -P Compute-1::NovaEnableRbdBackend=true;
      when: installer.deploy.type == 'plan'

    # EXCEPTION: - When a module breaks from multi-line use, add a comment to indicate it
    # The long line in this task fails when broken down
    - name: copy over common environment file (virt)
      local_action: >
          shell pushd {{ base_dir }}/khaleesi; rsync --delay-updates -F --compress --archive --rsh \
          "ssh -F ssh.config.ansible -S none -o StrictHostKeyChecking=no" \
          {{base_dir}}/khaleesi-settings/hardware_environments/common/plan-parameter-neutron-bridge.yaml undercloud:{{ instack_user_home }}/plan-parameter-neutron-bridge.yaml


**Rule: Using Quotes** - Use single quotes.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use single quotes throughout playbooks except when double quotes are required
for ``shell`` commands or enclosing ``when`` statements.

Examples::

    # BEST_PRACTICE_APPLIED
    - name: get floating ip address
      register: floating_ip_result
      shell: >
          source {{ instack_user_home }}/overcloudrc;
          neutron floatingip-show '{{ floating_ip.stdout }}' | grep 'ip_address' | sed -e 's/|//g';

    # EXCEPTION - shell command uses both single and double quotes
    - name: copy instackenv.json to root dir
      shell: >
          'ssh -t -o "StrictHostKeyChecking=no" {{ provisioner.host_cloud_user }}@{{ floating_ip.stdout }} \
          "sudo cp /home/{{ provisioner.host_cloud_user }}/instackenv.json /root/instackenv.json"'
      when: provisioner.host_cloud_user != 'root'

    # EXCEPTION - enclosing a ``when`` statement
    - name: copy instackenv.json to root dir
      shell: >
          'ssh -t -o "StrictHostKeyChecking=no" {{ provisioner.host_cloud_user }}@{{ floating_ip.stdout }} \
          "sudo cp /home/{{ provisioner.host_cloud_user }}/instackenv.json /root/instackenv.json"'
      when: "provisioner.host_cloud_user != {{ user }}"


**Rule: Order of Arguments** - Keep argument order consistent within a playbook.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The order of arguments is::

    tasks:
      - name:
        hosts:
        sudo:
        module:
        register:
        retries:
        delay:
        until:
        ignore_errors:
        with_items:
        when:

.. Warning:: While ``name`` is not required, it is an Ansible best practice, and a Khaleesi best
   practice, to `name all tasks <https://github.com/ansible/ansible/blob/devel/docsite/rst/playbooks_best_practices.rst#id38>`_.

Examples::

    # BEST_PRACTICE_APPLIED - polling
    - name: poll for heat stack-list to go to COMPLETE
      shell: >
          source {{ instack_user_home }}/stackrc;
          heat stack-list;
      register: heat_stack_list_result
      retries: 10
      delay: 180
      until: heat_stack_list_result.stdout.find("COMPLETE") != -1
      when: node_to_scale is defined

    # BEST_PRACTICE_APPLIED - looping through items
    - name: remove any yum repos not owned by rpm
      sudo: yes
      shell: rm -Rf /etc/yum.repos.d/{{ item }}
      ignore_errors: true
      with_items:
          - beaker-*


**Rule: Adding Workarounds** - Create bug reports and flags for all workarounds.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

More detailed information and examples on working with workarounds in Khaleesi can be found
in the documentation on `Handling Workarounds <http://khaleesi.readthedocs.org/en/master/development.html#handling-workarounds>`_.


**Rule: Ansible Modules** - Use Ansible modules over ``shell`` where available.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The generic ``shell`` module should be used only when there is not a suitable Ansible module
available to do the required steps. Use the  ``command`` module when a step requires a single
bash command.

Examples::

    # BEST_PRACTICE_APPLIED - using Ansible 'git' module rather than 'shell:  git clone'
    - name: clone openstack-virtual-baremetal repo
      git:
          repo=https://github.com/cybertron/openstack-virtual-baremetal/
          dest={{instack_user_home}}/openstack-virtual-baremetal

    # BEST_PRACTICE_APPLIED - using Openstack modules that have checks for redundancy or
    # existing elements
    - name: setup neutron network for floating ips
      register: public_network_uuid_result
      quantum_network:
          state: present
          auth_url: '{{ get_auth_url_result.stdout }}'
          login_username: admin
          login_password: '{{ get_admin_password_result.stdout }}'
          login_tenant_name: admin
          name: '{{ installer.network.name }}'
          provider_network_type: '{{ hw_env.network_type }}'
          provider_physical_network: '{{ hw_env.physical_network }}'
          provider_segmentation_id: '{{ hw_env.ExternalNetworkVlanID }}'
          router_external: yes
          shared: no

    # EXCEPTION - using  shell as there are no Ansible modules yet for updating nova quotas
    - name: set neutron subnet quota to unlimited
      ignore_errors: true
      shell: >
          source {{ instack_user_home }}/overcloudrc;
          neutron quota-update --subnet -1;
          neutron quota-update --network -1;


**Rule: Scripts** - Use scripts rather than shell for lengthy or complex bash operations.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Scripts can hide output details and debugging scripts requires the user to look in multiple
directories for the code involved. Consider using scripts over ``shell`` if the step in Ansible
requires multiple lines (more than ten), involves complex logic, or is called more than once.

Examples::

    # BEST_PRACTICE_APPLIED - calling Beaker checkout script,
    # keeps the complexity of Beaker provisioning in a standalone script
    - name: provision beaker machine with kerberos auth
      register: beaker_job_status
      shell: >
          chdir={{base_dir}}/khaleesi-settings
          {{base_dir}}/khaleesi-settings/beakerCheckOut.sh
          --arch={{ provisioner.beaker_arch }}
          --family={{ provisioner.beaker_family }}
          --distro={{ provisioner.beaker_distro }}
          --variant={{ provisioner.beaker_variant }}
          --hostrequire=hostlabcontroller={{ provisioner.host_lab_controller }}
          --task=/CoreOS/rhsm/Install/automatjon-keys
          --keyvalue=HVM=1
          --ks_meta=ksdevice=link
          --whiteboard={{ provisioner.whiteboard_message }}
          --job-group={{ provisioner.beaker_group }}
          --machine={{ lookup('env', 'BEAKER_MACHINE') }}
          --timeout=720;
      async: 7200
      poll: 180
      when: provisioner.beaker_password is not defined


**Rule - Roles** - Use roles for generic tasks which are applied across installers, provisioners, or testers.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Roles should be used to avoid code duplication. When using roles, take care to use debug steps and
print appropriate code output to allow users to trace the source of errors since the exact steps
are not visible directly in the playbook run. Please review the `Ansibles official best practices <http://docs.ansible.com/ansible/playbooks_best_practices.html#content-organization>`_
documentation for more information regarding role structure.

Examples::

    # BEST_PRACTICE_APPLIED - validate role that can be used with multiple installers
    https://github.com/redhat-openstack/khaleesi/tree/master/roles/validate_openstack



RDO-Manager Specific Best Practices
-----------------------------------

The following rules apply to RDO-Manager specific playbooks and roles.


**Rule: Step Placement** - Place a step under the playbook directory named for where it will be executed.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The RDO-Manager related playbooks have the following directory structure::

    |-- installer
         |-- rdo-manager
              |-- overcloud
              |-- undercloud
    | -- post-deploy
        |-- rdo-manager


These guidelines are used when deciding where to place new steps:

 * ``undercloud`` - any step that can be executed without the overcloud
 * ``overcloud`` - any step that is used to deploy the overcloud
 * ``post-deploy`` - always a standalone playbook - steps executed once the overcloud is deployed


**Rule: Idempotency** - Any step executed post setup should be idempotent.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

RDO-Manager has some set up steps that cannot be run multiple times without cleaning up the
environment. Any step added after setup should be able to rerun without causing damage.
*Defensive programming* conditions, that check for existence or availability etc. and modify
when or how a step is run, can be added to ensure playbooks remain idempotent.

Examples::

    # BEST_PRACTICE_APPLIED - using Ansible modules that check for existing elements
    - name: create provisioning network
      register: provision_network_uuid_result
      quantum_network:
          state: present
          auth_url: "{{ get_auth_url_result.stdout }}"
          login_username: admin
          login_password: "{{ get_admin_password_result.stdout }}"
          login_tenant_name: admin
          name: "{{ tmp.node_prefix }}provision"

    # BEST_PRACTICE_APPLIED - defensive programming,
    # ignoring errors from creating a flavor that already exists
    - name: create baremetal flavor
      shell: >
          source {{ instack_user_home }}/overcloudrc;
          nova flavor-create baremetal auto 6144 50 2;
      ignore_errors: true


Applying these Best Practices and Guidelines
--------------------------------------------

Before submitting a review for Khaleesi please review your changes to ensure they follow
with the best practices outlined above.


Contributing to this Guide
--------------------------
Additional best practices and suggestions for improvements to the coding standards are welcome.
To contribute to this guide, please review `contribution documentation <http://khaleesi.readthedocs.org/en/master/development.html>`_
and submit a review to `GerritHub <http://gerrithub.io/>`_.
