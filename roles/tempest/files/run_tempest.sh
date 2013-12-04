#!/bin/bash
pushd /var/lib/tempest
TEMPEST_PY26_NOSE_COMPAT=1 ./run_tests.sh -V -f -s -- --with-xunit

### test if the nosetests.xml exist in that case we don't treat the
### tempest run as a failure, rather let the xunit deal with the
### interpreting the nosetests.xml
test -f /var/lib/tempest/nosetests.xml
ret=$?

end=$(date +%Y-%m-%d-%H:%M:%S)
echo "Started at: ${start} Completed run at: ${end}"
#save conf and results to /var/log to be archived by packstack_extract_artifacts
cp /var/lib/tempest/etc/tempest.conf /var/log/
cp /var/lib/tempest/nosetests.xml /var/log/tempest_nosetests.xml
popd

exit $ret
