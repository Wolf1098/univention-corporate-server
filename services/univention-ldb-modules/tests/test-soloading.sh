#!/bin/sh
set -e

test="$(dirname "$0")"
base="${test}/.."

export PATH="${base}/bin${PATH:+:$PATH}"
export LDBDIR="${LDBDIR:-${base}}"
export LDB_MODULES_PATH="${base}/modules/ldb/"
export LDB_URL="${TEST_DATA_PREFIX:-.}/tdbtest.ldb"

rm -f "$LDB_URL"*

${VALGRIND:+$VALGRIND} ldbadd <<EOF
dn: @MODULES
@LIST: univention_samaccountname_ldap_check
EOF

testaccount=Administrator

# Test that the module loads successfully by adding a simple record
${VALGRIND:+$VALGRIND} ldbadd --trace <<EOF
dn: dc=test
dc: test
objectClass: domain
EOF

# Verify the record was added
${VALGRIND:+$VALGRIND} ldbsearch "(dc=test)" | grep "dc: test"

echo "SUCCESS"
