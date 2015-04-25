#!/bin/bash

TESTS_DIR="{{ tester.dir }}"
E_SKIP_CODE=999  # code used by tests to announce their skipping
E_FAILEDTESTS_CODE=42  # code used by us to say 'our execution was ok, but some tests failed'




header() {
  echo "====== $1 ======"
}

START="$(date "+%s")"
TOTAL=0
SKIPPED=0
FAILED=0

cd "$TESTS_DIR"
while read TEST; do
  [[ "$TEST" = "SetupTeardown.sh" || "$TEST" =~ sanity-net* ]] && continue

  TOTAL=$(( $TOTAL + 1 ))

  header "Running $TEST"
  time $TESTS_DIR/$TEST 2>&1
  STATUS=$?

  if [[ "$STATUS" = "$E_SKIP_CODE" ]]; then
    SKIPPED=$(( $SKIPPED + 1 ))
    header "$TEST: SKIPPED"
  elif [[ "$STATUS" != "0" ]]; then
    FAILED=$(( $FAILED + 1 ))
    header "$TEST: FAILED"
  else
    header "$TEST: PASSED"
  fi
done < <(ls -1 ${TESTS_DIR}/*.sh)

header "FINISHED"
header "TOTAL/FAILED/SKIPPED: $TOTAL/$FAILED/$SKIPPED"
header "IN $(( $(date "+%s") - $START )) SECONDS"

[[ $FAILED -gt 0 ]] && exit $E_FAILEDTESTS_CODE
exit 0
