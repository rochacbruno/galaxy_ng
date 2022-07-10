#!/bin/bash

# WARNING: DO NOT EDIT!
#
# This file was generated by plugin_template, and is managed by it. Please use
# './plugin-template --github galaxy_ng' to update this file.
#
# For more info visit https://github.com/pulp/plugin_template

set -mveuo pipefail

export PULP_URL="${PULP_URL:-https://pulp}"

# make sure this script runs at the repo root
cd "$(dirname "$(realpath -e "$0")")"/../../..

pip install twine wheel

export REPORTED_VERSION=$(http $PULP_URL/pulp/api/v3/status/ | jq --arg plugin galaxy --arg legacy_plugin galaxy_ng -r '.versions[] | select(.component == $plugin or .component == $legacy_plugin) | .version')
export DESCRIPTION="$(git describe --all --exact-match `git rev-parse HEAD`)"
if [[ $DESCRIPTION == 'tags/'$REPORTED_VERSION ]]; then
  export VERSION=${REPORTED_VERSION}
else
  export EPOCH="$(date +%s)"
  export VERSION=${REPORTED_VERSION}${EPOCH}
fi

export response=$(curl --write-out %{http_code} --silent --output /dev/null https://pypi.org/project/galaxy-ng-client/$VERSION/)

if [ "$response" == "200" ];
then
  echo "galaxy_ng client $VERSION has already been released. Installing from PyPI."
  docker exec pulp pip3 install galaxy-ng-client==$VERSION
  mkdir -p dist
  tar cvf python-client.tar ./dist
  exit
fi

cd ../pulp-openapi-generator
rm -rf galaxy_ng-client
./generate.sh galaxy_ng python $VERSION
cd galaxy_ng-client
python setup.py sdist bdist_wheel --python-tag py3
find . -name "*.whl" -exec docker exec pulp pip3 install /root/pulp-openapi-generator/galaxy_ng-client/{} \;
tar cvf ../../galaxy_ng/python-client.tar ./dist

find ./docs/* -exec sed -i 's/Back to README/Back to HOME/g' {} \;
find ./docs/* -exec sed -i 's/README//g' {} \;
cp README.md docs/index.md
sed -i 's/docs\///g' docs/index.md
find ./docs/* -exec sed -i 's/\.md//g' {} \;
tar cvf ../../galaxy_ng/python-client-docs.tar ./docs
exit $?
