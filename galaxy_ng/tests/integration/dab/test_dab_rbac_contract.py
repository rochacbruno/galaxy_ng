import pytest

# This tests the basic DAB RBAC contract using custom roles to do things


GALAXY_API_PATH_PREFIX = "/api/galaxy"  # cant import from settings on integration tests


def test_list_namespace_permissions(galaxy_client):
    gc = galaxy_client("admin")
    r = gc.get("_ui/v2/role_metadata/")
    assert "galaxy.namespace" in r["allowed_permissions"]
    allowed_perms = r["allowed_permissions"]["galaxy.namespace"]
    assert set(allowed_perms) == {
        "galaxy.change_namespace",
        "galaxy.delete_namespace",
        "galaxy.add_collectionimport",
        "galaxy.change_collectionimport",
        "galaxy.delete_collectionimport",
        "galaxy.upload_to_namespace",
        "galaxy.view_collectionimport",
        "galaxy.view_namespace",
    }


# look for the content_type choices
def test_role_definition_options(galaxy_client):
    gc = galaxy_client("admin")
    # TODO: add support for options in GalaxyClient in galaxykit
    galaxy_root = gc.galaxy_root
    api_prefix = galaxy_root[gc.galaxy_root.index('/api/'):]
    options_r = gc._http("options", api_prefix + "_ui/v2/role_definitions/")
    assert "actions" in options_r
    assert "POST" in options_r["actions"]
    assert "permissions" in options_r["actions"]["POST"]
    post_data = options_r["actions"]["POST"]
    assert "permissions" in post_data
    field_data = post_data["permissions"]
    assert "child" in field_data
    assert "choices" in field_data["child"]

    assert {
        "galaxy.change_namespace",
        "galaxy.add_namespace",
        "galaxy.delete_namespace",
        "galaxy.add_collectionimport",
        "galaxy.change_collectionimport",
        "galaxy.delete_collectionimport",
        "galaxy.upload_to_namespace",
        "galaxy.view_collectionimport",
        "galaxy.view_namespace",
        "shared.add_team",
        "shared.change_team",
        "shared.delete_team",
        "shared.view_team",
    }.issubset(set(item["value"] for item in field_data["child"]["choices"]))

    assert "content_type" in post_data
    field_data = post_data["content_type"]
    assert "choices" in field_data

    assert {
        "galaxy.collectionimport",
        "galaxy.namespace",
        "shared.team",
    }.issubset(set(item["value"] for item in field_data["choices"]))


# This is role data that works in both DAB and pulp roles
NS_FIXTURE_DATA = {
    "name": "galaxy.namespace_custom_system_role",
    "description": "A description for my new role from FIXTURE_DATA",
    "permissions": [
        "galaxy.change_namespace",
        "galaxy.delete_namespace",
        "galaxy.view_namespace",
        "galaxy.view_collectionimport",
    ],
}

DAB_ROLE_URL = "_ui/v2/role_definitions/"
PULP_ROLE_URL = "pulp/api/v3/roles/"


# these fixtures are function-scoped so they will be deleted
# deleting the role will delete all associated permissions
@pytest.fixture
def custom_role_creator(request, galaxy_client):
    def _rf(data, url_base=DAB_ROLE_URL):
        gc = galaxy_client("admin")
        list_r = gc.get(f"{url_base}?name={data['name']}")
        if list_r["count"] == 1:
            r = list_r["results"][0]
        elif list_r["count"] > 1:
            raise RuntimeError(f"Found too many {url_base} with expected name {data['name']}")
        else:
            r = gc.post(url_base, body=data)

        def delete_role():
            with pytest.raises(ValueError):
                if "id" in r:
                    gc.delete(f'{url_base}{r["id"]}/')
                elif "pulp_href" in r:
                    gc.delete(r["pulp_href"])
                else:
                    raise RuntimeError(f"Could not figure out how to delete {r}")

        request.addfinalizer(delete_role)
        return r

    return _rf


@pytest.fixture
def namespace(galaxy_client):
    gc = galaxy_client("admin")
    payload = {"name": "new_namespace"}
    ns = gc.post("_ui/v1/my-namespaces/", body=payload)
    yield ns
    with pytest.raises(ValueError):
        gc.delete(f"_ui/v1/my-namespaces/{ns['name']}/")


@pytest.mark.parametrize("by_api", ["dab", "pulp"])
def test_create_custom_namespace_system_admin_role(custom_role_creator, galaxy_client, by_api):
    if by_api == "dab":
        data = NS_FIXTURE_DATA.copy()
        data["content_type"] = None  # DAB-ism
        system_ns_role = custom_role_creator(data)
    else:
        system_ns_role = custom_role_creator(NS_FIXTURE_DATA.copy(), url_base=PULP_ROLE_URL)

    assert system_ns_role["name"] == NS_FIXTURE_DATA["name"]

    gc = galaxy_client("admin")
    list_r = gc.get(f"{DAB_ROLE_URL}?name={NS_FIXTURE_DATA['name']}")
    assert list_r["count"] == 1
    dab_role = list_r["results"][0]
    assert set(dab_role["permissions"]) == set(NS_FIXTURE_DATA["permissions"])

    list_r = gc.get(f"{PULP_ROLE_URL}?name={NS_FIXTURE_DATA['name']}")
    assert list_r["count"] == 1
    pulp_role = list_r["results"][0]
    assert set(pulp_role["permissions"]) == set(NS_FIXTURE_DATA["permissions"])


def test_give_user_custom_role_system(galaxy_client, custom_role_creator):
    system_ns_role = custom_role_creator(NS_FIXTURE_DATA)
    gc = galaxy_client("admin")
    user_r = gc.get("_ui/v2/users/")
    assert user_r["count"] > 0
    user = user_r["results"][0]
    gc.post(
        "_ui/v2/role_user_assignments/",
        body={"role_definition": system_ns_role["id"], "user": user["id"]},
    )
    # TODO: verify that assignment is seen in DAB and pulp APIs
    # TODO: make a request as the user and see that it works


def test_give_team_custom_role_system(galaxy_client, custom_role_creator):
    system_ns_role = custom_role_creator(NS_FIXTURE_DATA)
    gc = galaxy_client("admin")
    teams_r = gc.get("_ui/v2/teams/")
    assert teams_r["count"] > 0
    team = teams_r["results"][0]
    gc.post(
        "_ui/v2/role_team_assignments/",
        body={"role_definition": system_ns_role["id"], "team": team["id"]},
    )


# TODO: test making a user a member of a team (supported locally? unclear)
# TODO: test that a user can get a permission via membership in a team


def assert_assignments(gc, user, namespace, expected=0):
    # Assure the assignment shows up in the pulp API
    r = gc.get(f"_ui/v1/my-namespaces/{namespace['name']}/")
    assert len(r["users"]) == expected

    # Assure the assignment shows up in the DAB RBAC API
    r = gc.get(
        f"_ui/v2/role_user_assignments/?user={user['id']}&object_id={namespace['id']}"
    )
    assert r["count"] == expected

    if expected > 0:
        # Ensure summary_fields is populated with expected sub keys
        expected_fields = {"created_by", "role_definition", "user", "content_objet"}

        summary_fields = r["results"][0]["summary_fields"]
        related = r["results"][0]["related"]

        assert expected_fields.issubset(summary_fields)
        assert expected_fields.issubset(related)

        # assert each entry has at least the id field
        for field in expected_fields:
            assert "id" in summary_fields[field]

        # assert related includes relative urls
        for field in expected_fields:
            assert related[field].startswith(GALAXY_API_PATH_PREFIX)


@pytest.mark.parametrize("by_api", ["dab", "pulp"])
def test_give_custom_role_object(
    request, galaxy_client, custom_role_creator, namespace, by_api, random_username
):
    data = NS_FIXTURE_DATA.copy()
    data["name"] = "galaxy.namespace_custom_object_role"
    data["content_type"] = "galaxy.namespace"
    custom_obj_role = custom_role_creator(data)

    gc = galaxy_client("admin")
    user_r = gc.get("_ui/v2/users/")
    assert user_r["count"] > 0
    user = user_r["results"][0]

    # sanity - assignments should not exist at start of this test
    assert_assignments(gc, user, namespace, 0)

    # Give the user permission to the namespace object
    dab_assignment = None
    if by_api == "dab":
        dab_assignment = gc.post(
            "_ui/v2/role_user_assignments/",
            body={
                "role_definition": custom_obj_role["id"],
                "user": user["id"],
                "object_id": str(namespace["id"]),
            },
        )
    else:
        payload = {
            "name": namespace["name"],
            "users": [
                {
                    "id": user["id"],
                    "object_roles": [custom_obj_role["name"]],
                }
            ],
        }
        gc.put(f"_ui/v1/my-namespaces/{namespace['name']}/", body=payload)

    # TODO: make a request as the user and see that it works

    assert_assignments(gc, user, namespace, 1)

    # Remove the permission from before
    if by_api == "dab":
        with pytest.raises(ValueError):
            gc.delete(f"_ui/v2/role_user_assignments/{dab_assignment['id']}/")
    else:
        payload = {
            "name": namespace["name"],
            "users": [],
        }
        gc.put(f"_ui/v1/my-namespaces/{namespace['name']}/", body=payload)

    assert_assignments(gc, user, namespace, 0)
