echo $delorean_current_hash
#ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i ~/.ssh/rhos-ci -p 330 promoter@$DELOREAN_HOST "sudo /usr/local/bin/promote.sh $HASH" $RDO_VERSION || true
