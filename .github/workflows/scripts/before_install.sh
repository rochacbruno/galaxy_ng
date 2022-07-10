#!/usr/bin/env bash

# WARNING: DO NOT EDIT!
#
# This file was generated by plugin_template, and is managed by it. Please use
# './plugin-template --github galaxy_ng' to update this file.
#
# For more info visit https://github.com/pulp/plugin_template

# make sure this script runs at the repo root
cd "$(dirname "$(realpath -e "$0")")"/../../..

set -mveuo pipefail

if [ "${GITHUB_REF##refs/heads/}" = "${GITHUB_REF}" ]
then
  BRANCH_BUILD=0
else
  BRANCH_BUILD=1
  BRANCH="${GITHUB_REF##refs/heads/}"
fi
if [ "${GITHUB_REF##refs/tags/}" = "${GITHUB_REF}" ]
then
  TAG_BUILD=0
else
  TAG_BUILD=1
  BRANCH="${GITHUB_REF##refs/tags/}"
fi

COMMIT_MSG=$(git log --format=%B --no-merges -1)
export COMMIT_MSG

if [[ "$TEST" == "upgrade" ]]; then
  pip install -r functest_requirements.txt
  git checkout -b ci_upgrade_test
  cp -R .github /tmp/.github
  cp -R .ci /tmp/.ci
  git checkout $FROM_GALAXY_NG_BRANCH
  rm -rf .ci .github
  cp -R /tmp/.github .
  cp -R /tmp/.ci .
fi

if [[ "$TEST" == "plugin-from-pypi" ]]; then
  COMPONENT_VERSION=$(http https://pypi.org/pypi/galaxy-ng/json | jq -r '.info.version')
else
  COMPONENT_VERSION=$(sed -ne "s/\s*version.*=.*['\"]\(.*\)['\"][\s,]*/\1/p" setup.py)
fi
mkdir .ci/ansible/vars || true
echo "---" > .ci/ansible/vars/main.yaml
echo "legacy_component_name: galaxy_ng" >> .ci/ansible/vars/main.yaml
echo "component_name: galaxy" >> .ci/ansible/vars/main.yaml
echo "component_version: '${COMPONENT_VERSION}'" >> .ci/ansible/vars/main.yaml

export PRE_BEFORE_INSTALL=$PWD/.github/workflows/scripts/pre_before_install.sh
export POST_BEFORE_INSTALL=$PWD/.github/workflows/scripts/post_before_install.sh

if [ -f $PRE_BEFORE_INSTALL ]; then
  source $PRE_BEFORE_INSTALL
fi

if [[ -n $(echo -e $COMMIT_MSG | grep -P "Required PR:.*" | grep -v "https") ]]; then
  echo "Invalid Required PR link detected in commit message. Please use the full https url."
  exit 1
fi

if [ "$GITHUB_EVENT_NAME" = "pull_request" ] || [ "${BRANCH_BUILD}" = "1" -a "${BRANCH}" != "master" ]
then
  export PULPCORE_PR_NUMBER=$(echo $COMMIT_MSG | grep -oP 'Required\ PR:\ https\:\/\/github\.com\/pulp\/pulpcore\/pull\/(\d+)' | awk -F'/' '{print $7}')
  export PULP_SMASH_PR_NUMBER=$(echo $COMMIT_MSG | grep -oP 'Required\ PR:\ https\:\/\/github\.com\/pulp\/pulp-smash\/pull\/(\d+)' | awk -F'/' '{print $7}')
  export PULP_OPENAPI_GENERATOR_PR_NUMBER=$(echo $COMMIT_MSG | grep -oP 'Required\ PR:\ https\:\/\/github\.com\/pulp\/pulp-openapi-generator\/pull\/(\d+)' | awk -F'/' '{print $7}')
  export PULP_CLI_PR_NUMBER=$(echo $COMMIT_MSG | grep -oP 'Required\ PR:\ https\:\/\/github\.com\/pulp\/pulp-cli\/pull\/(\d+)' | awk -F'/' '{print $7}')
  export PULP_ANSIBLE_PR_NUMBER=$(echo $COMMIT_MSG | grep -oP 'Required\ PR:\ https\:\/\/github\.com\/pulp\/pulp_ansible\/pull\/(\d+)' | awk -F'/' '{print $7}')
  export PULP_CONTAINER_PR_NUMBER=$(echo $COMMIT_MSG | grep -oP 'Required\ PR:\ https\:\/\/github\.com\/pulp\/pulp_container\/pull\/(\d+)' | awk -F'/' '{print $7}')
  export GALAXY_IMPORTER_PR_NUMBER=$(echo $COMMIT_MSG | grep -oP 'Required\ PR:\ https\:\/\/github\.com\/ansible\/galaxy-importer\/pull\/(\d+)' | awk -F'/' '{print $7}')
  echo $COMMIT_MSG | sed -n -e 's/.*CI Base Image:\s*\([-_/[:alnum:]]*:[-_[:alnum:]]*\).*/ci_base: "\1"/p' >> .ci/ansible/vars/main.yaml
else
  export PULPCORE_PR_NUMBER=
  export PULP_SMASH_PR_NUMBER=
  export PULP_OPENAPI_GENERATOR_PR_NUMBER=
  export PULP_CLI_PR_NUMBER=
  export PULP_ANSIBLE_PR_NUMBER=
  export PULP_CONTAINER_PR_NUMBER=
  export GALAXY_IMPORTER_PR_NUMBER=
  export CI_BASE_IMAGE=
fi


cd ..


git clone --depth=1 https://github.com/pulp/pulp-smash.git

if [ -n "$PULP_SMASH_PR_NUMBER" ]; then
  cd pulp-smash
  git fetch --depth=1 origin pull/$PULP_SMASH_PR_NUMBER/head:$PULP_SMASH_PR_NUMBER
  git checkout $PULP_SMASH_PR_NUMBER
  cd ..
fi

pip install --upgrade --force-reinstall ./pulp-smash


git clone --depth=1 https://github.com/pulp/pulp-openapi-generator.git
if [ -n "$PULP_OPENAPI_GENERATOR_PR_NUMBER" ]; then
  cd pulp-openapi-generator
  git fetch origin pull/$PULP_OPENAPI_GENERATOR_PR_NUMBER/head:$PULP_OPENAPI_GENERATOR_PR_NUMBER
  git checkout $PULP_OPENAPI_GENERATOR_PR_NUMBER
  cd ..
fi



git clone --depth=1 https://github.com/pulp/pulpcore.git --branch 3.18.1

cd pulpcore

if [ -n "$PULPCORE_PR_NUMBER" ]; then
  git fetch --depth=1 origin pull/$PULPCORE_PR_NUMBER/head:$PULPCORE_PR_NUMBER
  git checkout $PULPCORE_PR_NUMBER
fi
cd ..


git clone --depth=1 https://github.com/pulp/pulp_ansible.git --branch 0.13
cd pulp_ansible

if [ -n "$PULP_ANSIBLE_PR_NUMBER" ]; then
  git fetch --depth=1 origin pull/$PULP_ANSIBLE_PR_NUMBER/head:$PULP_ANSIBLE_PR_NUMBER
  git checkout $PULP_ANSIBLE_PR_NUMBER
fi

cd ..

git clone --depth=1 https://github.com/pulp/pulp_container.git --branch 2.10.2
cd pulp_container

if [ -n "$PULP_CONTAINER_PR_NUMBER" ]; then
  git fetch --depth=1 origin pull/$PULP_CONTAINER_PR_NUMBER/head:$PULP_CONTAINER_PR_NUMBER
  git checkout $PULP_CONTAINER_PR_NUMBER
fi

cd ..

git clone --depth=1 https://github.com/ansible/galaxy-importer.git --branch v0.4.2
cd galaxy-importer

if [ -n "$GALAXY_IMPORTER_PR_NUMBER" ]; then
  git fetch --depth=1 origin pull/$GALAXY_IMPORTER_PR_NUMBER/head:$GALAXY_IMPORTER_PR_NUMBER
  git checkout $GALAXY_IMPORTER_PR_NUMBER
fi

cd ..



# Intall requirements for ansible playbooks
pip install docker netaddr boto3 ansible

for i in {1..3}
do
  ansible-galaxy collection install "amazon.aws:1.5.0" && s=0 && break || s=$? && sleep 3
done
if [[ $s -gt 0 ]]
then
  echo "Failed to install amazon.aws"
  exit $s
fi

cd galaxy_ng

if [ -f $POST_BEFORE_INSTALL ]; then
  source $POST_BEFORE_INSTALL
fi
