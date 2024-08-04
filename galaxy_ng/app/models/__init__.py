from .aiindex import AIIndexDenyList
from .auth import Group, User
from .collectionimport import CollectionImport
from .config import Setting
from .container import (
    ContainerDistribution,
    ContainerDistroReadme,
    ContainerNamespace,
    ContainerRegistryRemote,
    ContainerRegistryRepos,
)
from .namespace import Namespace, NamespaceLink
from .organization import Organization, Team
from .synclist import SyncList

from pulp_ansible.app.models import (
    AnsibleCollectionDeprecated,
    AnsibleDistribution,
    AnsibleNamespace,
    AnsibleNamespaceMetadata,
    AnsibleRepository,
    Collection,
    CollectionRemote,
    CollectionVersion,
    CollectionVersionSignature,
    Tag,
)

from ansible_base.rbac import permission_registry

__all__ = (
    # aiindex
    "AIIndexDenyList",
    # auth
    "Group",
    "User",
    # collectionimport
    "CollectionImport",
    # config
    "Setting",
    # container
    "ContainerDistribution",
    "ContainerDistroReadme",
    "ContainerNamespace",
    "ContainerRegistryRemote",
    "ContainerRegistryRepos",
    # namespace
    "Namespace",
    "NamespaceLink",
    # organization
    "Organization",
    "Team",
    # synclist
    "SyncList",
)

permission_registry.register(
    AnsibleCollectionDeprecated, parent_field_name=None
)
permission_registry.register(
    AnsibleDistribution, parent_field_name=None
)
permission_registry.register(
    AnsibleNamespace, parent_field_name=None
)
permission_registry.register(
    AnsibleNamespaceMetadata, parent_field_name=None
)
permission_registry.register(
    AnsibleRepository, parent_field_name=None
)
permission_registry.register(
    Collection, parent_field_name=None
)
permission_registry.register(
    CollectionRemote, parent_field_name=None
)
permission_registry.register(
    CollectionVersion, parent_field_name=None
)
permission_registry.register(
    CollectionVersionSignature, parent_field_name=None
)
permission_registry.register(
    Tag, parent_field_name=None
)

permission_registry.register(
    Namespace, parent_field_name=None
)
permission_registry.register(
    NamespaceLink, parent_field_name=None
)
permission_registry.register(
    ContainerDistribution, parent_field_name=None
)
permission_registry.register(
    ContainerDistroReadme, parent_field_name=None
)
permission_registry.register(
    ContainerNamespace, parent_field_name=None
)
permission_registry.register(
    ContainerRegistryRemote, parent_field_name=None
)
permission_registry.register(
    ContainerRegistryRepos, parent_field_name=None
)
permission_registry.register(
    CollectionImport, parent_field_name='namespace'
)
