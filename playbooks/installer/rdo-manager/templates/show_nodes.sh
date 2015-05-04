source {{ instack_user_home }}/stackrc;
node_ids=$(ironic node-list | tail -n +4 | head -n -1 | awk '{print $2}');
for node_id in $node_ids; do ironic node-show $node_id; done;
