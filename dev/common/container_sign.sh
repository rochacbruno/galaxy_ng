#!/usr/bin/env bash

export PULP_SIGNING_KEY_FINGERPRINT=$(gpg --show-keys --with-colons --with-fingerprint /tmp/ansible-sign.key | awk -F: '$1 == "fpr" {print $10;}' | head -n1)

 MANIFEST_PATH1=$1
 FINGEPRINT="$PULP_SIGNING_KEY_FINGERPRINT"
 IMAGE_REFERENCE="$REFERENCE"
 SIGNATURE_PATH="$SIG_PATH"

 # Create container signature
 skopeo standalone-sign $MANIFEST_PATH $IMAGE_REFERENCE $FINGEPRINT --output $SIGNATURE_PATH
 # Check the exit status
 STATUS=$?
 if [ $STATUS -eq 0 ]; then
   echo {\"signature_path\": \"$SIGNATURE_PATH\"}
 else
   exit $STATUS
 fi
