find ./playbooks -name '*.yml'| xargs -n1  ansible-playbook --syntax-check --list-tasks -i local_hosts 
