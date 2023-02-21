"""Tests related to RBAC roles.

See: https://issues.redhat.com/browse/AAH-957
"""
import logging
import pytest
import requests

from .rbac_actions.utils import (
    ADMIN_CREDENTIALS,
    ADMIN_USER,
    ADMIN_PASSWORD,
    API_ROOT,
    NAMESPACE,
    PASSWORD,
    create_group_with_user_and_role,
    create_user,
    gen_string,
    del_user,
    del_group,
    ReusableCollection,
    ReusableContainerRegistry,
    ReusableRemoteContainer,
    ReusableLocalContainer,
)

from .rbac_actions.auth import (
    view_groups, delete_groups, add_groups, change_groups,
    add_pulp_groups, delete_pulp_groups, view_pulp_groups,
    view_users, delete_users, add_users, change_users,
    view_role, delete_role, add_role, change_role,
)
from .rbac_actions.misc import view_tasks
from .rbac_actions.collections import (
    create_collection_namespace,
    change_collection_namespace,
    delete_collection_namespace,
    upload_collection_to_namespace,
    delete_collection,
    configure_collection_sync,
    launch_collection_sync,
    view_sync_configuration,
    approve_collections,
    reject_collections,
    deprecate_collections,
    undeprecate_collections,

    # ansible repository
    view_ansible_repository,
    add_ansible_repository,
    modify_ansible_repository,
    rebuild_metadata_ansible_repository,
    sign_ansible_repository,
    sync_ansible_repository,
    delete_ansible_repository,

    # ansible repository version
    view_ansible_repository_version,
    # rebuild_metadata_ansible_repository_version,
    repair_ansible_repository_version,
    delete_ansible_repository_version,

    # ansible distribution
    view_ansible_distribution,
    add_ansible_distribution,
    change_ansible_distribution,
    delete_ansible_distribution,

    # ansible collection remote
    view_ansible_remote,
    add_ansible_remote,
    change_ansible_remote,
    delete_ansible_remote
)
from .rbac_actions.exec_env import (
    # Remotes
    create_ee_remote,
    update_ee_remote,
    sync_remote_ee,

    # Registries
    delete_ee_registry,
    index_ee_registry,
    update_ee_registry,
    create_ee_registry,

    # Containers
    delete_ee,
    change_ee_description,
    change_ee_readme,
    create_ee_local,
    create_ee_in_existing_namespace,
    push_updates_to_existing_ee,
    change_ee_tags,

    # Container namespace
    ee_namespace_list_roles,
    ee_namespace_my_permissions,
    ee_namespace_add_role,
    ee_namespace_remove_role
)

log = logging.getLogger(__name__)

# Order is important, CRU before D actions
GLOBAL_ACTIONS = [

    # AUTHENTICATION
    add_groups,
    view_groups,
    change_groups,
    delete_groups,
    add_users,
    change_users,
    view_users,
    delete_users,
    add_role,
    change_role,
    view_role,
    delete_role,

    # COLLECTIONS
    create_collection_namespace,
    change_collection_namespace,
    delete_collection_namespace,
    upload_collection_to_namespace,
    delete_collection,
    configure_collection_sync,
    launch_collection_sync,
    view_sync_configuration,
    approve_collections,
    reject_collections,
    deprecate_collections,
    undeprecate_collections,

    # EEs
    # Remotes
    create_ee_remote,
    update_ee_remote,
    sync_remote_ee,

    # Registries
    delete_ee_registry,
    index_ee_registry,
    update_ee_registry,
    create_ee_registry,

    # Containers
    delete_ee,
    change_ee_description,
    change_ee_readme,
    create_ee_local,
    create_ee_in_existing_namespace,
    push_updates_to_existing_ee,
    change_ee_tags,

    # MISC
    view_tasks,

    # ansible repository
    view_ansible_repository,
    add_ansible_repository,
    modify_ansible_repository,
    rebuild_metadata_ansible_repository,
    sign_ansible_repository,
    sync_ansible_repository,
    delete_ansible_repository,

    # ansible repository version
    view_ansible_repository_version,
    # FIXME: https://github.com/pulp/pulp_ansible/pull/1311
    # rebuild_metadata_ansible_repository_version,
    repair_ansible_repository_version,
    delete_ansible_repository_version,

    # ansible distribution
    view_ansible_distribution,
    add_ansible_distribution,
    change_ansible_distribution,
    delete_ansible_distribution,

    # ansible collection remote
    view_ansible_remote,
    add_ansible_remote,
    change_ansible_remote,
    delete_ansible_remote
]

# TODO: Update object tests to include delete actions
OBJECT_ACTIONS = [
    change_collection_namespace,
    upload_collection_to_namespace,
    deprecate_collections,
    undeprecate_collections,
    change_ee_description,
    change_ee_readme,
    create_ee_in_existing_namespace,
    push_updates_to_existing_ee,
    change_ee_tags,
    sync_remote_ee,

    ee_namespace_list_roles,
    ee_namespace_my_permissions,
    ee_namespace_add_role,
    ee_namespace_remove_role
]

OBJECT_ROLES_TO_TEST = {
    # COLLECTIONS
    "galaxy.collection_namespace_owner": {
        change_collection_namespace,
        upload_collection_to_namespace,
        deprecate_collections,
        undeprecate_collections,
    },
    "galaxy.collection_publisher": {
        create_collection_namespace,
        change_collection_namespace,
        upload_collection_to_namespace,
        deprecate_collections,
        undeprecate_collections,
    },

    # EEs
    "galaxy.execution_environment_publisher": {
        create_ee_remote,
        update_ee_remote,
        sync_remote_ee,
        change_ee_description,
        change_ee_readme,
        create_ee_local,
        create_ee_in_existing_namespace,
        push_updates_to_existing_ee,
        change_ee_tags,
        ee_namespace_list_roles,
        ee_namespace_my_permissions,
        ee_namespace_add_role,
        ee_namespace_remove_role
    },
    "galaxy.execution_environment_namespace_owner": {
        update_ee_remote,
        change_ee_description,
        change_ee_readme,
        create_ee_in_existing_namespace,
        push_updates_to_existing_ee,
        change_ee_tags,
        sync_remote_ee,
        ee_namespace_list_roles,
        ee_namespace_my_permissions,
        ee_namespace_add_role,
        ee_namespace_remove_role
    },
    "galaxy.execution_environment_collaborator": {
        update_ee_remote,
        change_ee_description,
        change_ee_readme,
        push_updates_to_existing_ee,
        change_ee_tags,
        sync_remote_ee,
        ee_namespace_my_permissions
    },


}

ROLES_TO_TEST = {
    "galaxy.content_admin": {
        # COLLECTIONS
        create_collection_namespace,
        change_collection_namespace,
        delete_collection_namespace,
        upload_collection_to_namespace,
        delete_collection,
        configure_collection_sync,
        launch_collection_sync,
        view_sync_configuration,
        approve_collections,
        reject_collections,
        deprecate_collections,
        undeprecate_collections,

        # ansible repository
        view_ansible_repository,
        add_ansible_repository,
        modify_ansible_repository,
        rebuild_metadata_ansible_repository,
        sign_ansible_repository,
        sync_ansible_repository,
        delete_ansible_repository,

        # ansible repository version
        view_ansible_repository_version,
        # rebuild_metadata_ansible_repository_version,
        repair_ansible_repository_version,
        delete_ansible_repository_version,

        # ansible distribution
        view_ansible_distribution,
        add_ansible_distribution,
        change_ansible_distribution,
        delete_ansible_distribution,

        # ansible collection remote
        view_ansible_remote,
        add_ansible_remote,
        change_ansible_remote,
        delete_ansible_remote,

        # EEs
        # Remotes
        create_ee_remote,
        update_ee_remote,
        sync_remote_ee,

        # Registries
        delete_ee_registry,
        index_ee_registry,
        update_ee_registry,
        create_ee_registry,

        # Containers
        delete_ee,
        change_ee_description,
        change_ee_readme,
        create_ee_local,
        create_ee_in_existing_namespace,
        push_updates_to_existing_ee,
        change_ee_tags,

        # Container namespace
        ee_namespace_list_roles,
        ee_namespace_my_permissions,
        ee_namespace_add_role,
        ee_namespace_remove_role

    },
    "galaxy.collection_admin": {
        create_collection_namespace,
        change_collection_namespace,
        upload_collection_to_namespace,
        delete_collection,
        delete_collection_namespace,
        configure_collection_sync,
        launch_collection_sync,
        approve_collections,
        reject_collections,
        deprecate_collections,
        undeprecate_collections,

        # ansible repository
        view_ansible_repository,
        add_ansible_repository,
        modify_ansible_repository,
        rebuild_metadata_ansible_repository,
        sign_ansible_repository,
        sync_ansible_repository,
        delete_ansible_repository,

        # ansible repository version
        view_ansible_repository_version,
        # rebuild_metadata_ansible_repository_version,
        repair_ansible_repository_version,
        delete_ansible_repository_version,

        # ansible distribution
        view_ansible_distribution,
        add_ansible_distribution,
        change_ansible_distribution,
        delete_ansible_distribution,

        # ansible collection remote
        view_ansible_remote,
        add_ansible_remote,
        change_ansible_remote,
        delete_ansible_remote
    },
    "galaxy.collection_curator": {
        configure_collection_sync,
        launch_collection_sync,
        approve_collections,
        reject_collections,

        # ansible repository
        view_ansible_repository,
        add_ansible_repository,
        modify_ansible_repository,
        rebuild_metadata_ansible_repository,
        sign_ansible_repository,
        sync_ansible_repository,
        delete_ansible_repository,

        # ansible repository version
        view_ansible_repository_version,
        # rebuild_metadata_ansible_repository_version,
        repair_ansible_repository_version,
        delete_ansible_repository_version,

        # ansible distribution
        view_ansible_distribution,
        add_ansible_distribution,
        change_ansible_distribution,
        delete_ansible_distribution,

        # ansible collection remote
        view_ansible_remote,
        add_ansible_remote,
        change_ansible_remote,
        delete_ansible_remote
    },
    "galaxy.execution_environment_admin": {
        # EEs
        # Remotes
        create_ee_remote,
        update_ee_remote,
        sync_remote_ee,

        # Registries
        delete_ee_registry,
        index_ee_registry,
        update_ee_registry,
        create_ee_registry,

        # Containers
        delete_ee,
        change_ee_description,
        change_ee_readme,
        create_ee_local,
        create_ee_in_existing_namespace,
        push_updates_to_existing_ee,
        change_ee_tags,

        # Container namespace
        ee_namespace_list_roles,
        ee_namespace_my_permissions,
        ee_namespace_add_role,
        ee_namespace_remove_role

    },
    "galaxy.group_admin": {
        add_groups,
        change_groups,
        delete_groups,
        view_role,
        add_pulp_groups,
        delete_pulp_groups,
        view_pulp_groups,
    },
    "galaxy.user_admin": {
        add_users,
        view_users,
        change_users,
        delete_users,
    },
    "galaxy.task_admin": {}
}
ROLES_TO_TEST.update(OBJECT_ROLES_TO_TEST)

ACTIONS_FOR_ALL_USERS = {
    view_sync_configuration,
    view_groups,
    view_tasks,
    view_role,
}


REUSABLE_EXTRA = {}


# initialize the extra objects once for all the tests. This saves ~20 seconds per test
def _get_reusable_extras():
    global REUSABLE_EXTRA

    if len(REUSABLE_EXTRA) == 0:
        _registry = ReusableContainerRegistry(gen_string())
        _registry_pk = _registry.get_registry()["id"]

        REUSABLE_EXTRA = {
            "collection": ReusableCollection(gen_string()),
            "registry": _registry,
            "remote_ee": ReusableRemoteContainer(gen_string(), _registry_pk),
            "local_ee": ReusableLocalContainer(gen_string()),
        }

    return REUSABLE_EXTRA


@pytest.mark.rbac_roles
@pytest.mark.standalone_only
@pytest.mark.parametrize("role", ROLES_TO_TEST)
def test_global_role_actions(role):
    USERNAME = f"{NAMESPACE}_user_{gen_string()}"

    user = create_user(USERNAME, PASSWORD)
    group = create_group_with_user_and_role(user, role)
    group_id = group['id']

    expected_allows = ROLES_TO_TEST[role]

    extra = _get_reusable_extras()

    failures = []
    # Test global actions
    for action in GLOBAL_ACTIONS:
        expect_pass = action in expected_allows or action in ACTIONS_FOR_ALL_USERS
        try:
            action(user, PASSWORD, expect_pass, extra)
        except AssertionError:
            failures.append(action.__name__)

    # cleanup user, group
    requests.delete(f"{API_ROOT}_ui/v1/users/{user['id']}/", auth=ADMIN_CREDENTIALS)
    requests.delete(f"{API_ROOT}_ui/v1/groups/{group_id}/", auth=ADMIN_CREDENTIALS)

    del_user(user['id'])
    del_group(group_id)

    assert failures == []


@pytest.mark.rbac_roles
@pytest.mark.standalone_only
def test_object_role_actions():
    registry = ReusableContainerRegistry(gen_string())
    registry_pk = registry.get_registry()["id"]

    users_and_groups = {}
    col_groups = []
    ee_groups = []

    # Create user/group for each role
    # Populate collection/ee groups for object assignment
    for role in OBJECT_ROLES_TO_TEST:
        USERNAME = f"{NAMESPACE}_user_{gen_string()}"
        user = create_user(USERNAME, PASSWORD)
        group = create_group_with_user_and_role(user, role)
        users_and_groups[role] = {
            'user': user,
            'group': group
        }
        if role in ['galaxy.collection_namespace_owner']:
            col_groups.append({
                'id': users_and_groups[role]['group']['id'],
                'name': users_and_groups[role]['group']['name'],
                'object_roles': [role]
            })
        if role in [
            'galaxy.execution_environment_namespace_owner',
            'galaxy.execution_environment_collaborator'
        ]:
            ee_groups.append({
                'id': users_and_groups[role]['group']['id'],
                'name': users_and_groups[role]['group']['name'],
                'object_roles': [role]
            })

    extra = {
        "collection": ReusableCollection(gen_string(), groups=col_groups),
        "registry": registry,
        "remote_ee": ReusableRemoteContainer(gen_string(), registry_pk, groups=ee_groups),
        "local_ee": ReusableLocalContainer(gen_string()),
    }

    for role in OBJECT_ROLES_TO_TEST:
        expected_allows = ROLES_TO_TEST[role]

        failures = []
        # Test object actions
        for action in OBJECT_ACTIONS:
            expect_pass = action in expected_allows or action in ACTIONS_FOR_ALL_USERS
            try:
                action(users_and_groups[role]['user'], PASSWORD, expect_pass, extra)
            except AssertionError:
                failures.append(f'{role}:{action.__name__}')

    # cleanup user, group
    for role in OBJECT_ROLES_TO_TEST:
        del_user(users_and_groups[role]['user']['id'])
        del_group(users_and_groups[role]['group']['id'])

    del extra['collection']
    del extra['registry']
    del extra['remote_ee']
    del extra['local_ee']

    assert failures == []


@pytest.mark.rbac_roles
@pytest.mark.standalone_only
def test_role_actions_for_admin():
    extra = _get_reusable_extras()
    failures = []

    # Test global actions
    for action in GLOBAL_ACTIONS:
        try:
            action({'username': ADMIN_USER}, ADMIN_PASSWORD, True, extra)
        except AssertionError:
            failures.append(action.__name__)

    assert failures == []