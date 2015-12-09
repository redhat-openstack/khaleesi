export PROMOTE_HASH=`echo $delorean_current_hash | awk -F '/' '{ print $3}'`

ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i ~/.ssh/rhos-ci -p 3300 promoter@$DELOREAN_HOST "sudo /usr/local/bin/promote.sh $PROMOTE_HASH" $RDO_VERSION || true