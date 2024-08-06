import json
import os

import pytest

from galaxykit.client import GalaxyClient
from galaxykit.collections import upload_test_collection


pytestmark = pytest.mark.qa  # noqa: F821


@pytest.mark.deployment_standalone
@pytest.mark.skipif(
    not os.getenv("ENABLE_DAB_TESTS"),
    reason="Skipping test because ENABLE_DAB_TESTS is not set"
)
def test_dab_rbac_namespace_owner_by_user(galaxy_client, random_namespace, random_username):
    """Tests the galaxy.system_auditor role can be added to a user and has the right perms."""

    gc = galaxy_client("admin", ignore_cache=True)

    # create the user in the proxy ...
    gc.post(
        "/api/gateway/v1/users/",
        body=json.dumps({"username": random_username, "password": "redhat1234"})
    )

    # get the user's galaxy level details ...
    auth = {'username': random_username, 'password': 'redhat1234'}
    ugc = GalaxyClient(gc.galaxy_root, auth=auth)
    me_ds = ugc.get('_ui/v1/me/')

    # find the role for namespace owner ...
    rd = gc.get('_ui/v2/role_definitions/?name=galaxy.collection_namespace_owner')
    role_id = rd['results'][0]['id']

    # assign the user role ...
    payload = {
        'user': me_ds['id'],
        'role_definition': role_id,
        'content_type': 'galaxy.namespace',
        'object_id': random_namespace['id'],
    }
    gc.post('_ui/v2/role_user_assignments/', body=payload)

    # try to upload a collection as the user...
    upload_test_collection(ugc, namespace=random_namespace['name'])
