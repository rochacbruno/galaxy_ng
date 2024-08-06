from pulpcore.plugin import PulpPluginAppConfig


class PulpGalaxyPluginAppConfig(PulpPluginAppConfig):
    """Entry point for the galaxy plugin."""

    name = "galaxy_ng.app"
    label = "galaxy"
    version = "4.10.0dev"
    python_package_name = "galaxy-ng"

    def ready(self):
        super().ready()
        from .signals import handlers  # noqa
        add_dab_summary_fields_to_models()


def add_dab_summary_fields_to_models():
    """DAB Expects Content Types to expose summary_fields method.

    Apps must be ready to start importing and patching models.
    """
    from ansible_base.lib.utils.models import user_summary_fields
    from pulp_ansible.app import models as pulp_ansible_models
    from pulp_container.app import models as pulp_container_models
    from pulpcore.plugin import models as pulpcore_models

    from galaxy_ng.app.models import collectionimport as galaxy_collectionimport_models
    from galaxy_ng.app.models import container as galaxy_container_models
    from galaxy_ng.app.models import namespace as galaxy_namespace_models
    from galaxy_ng.app.models.auth import User

    User.add_to_class('summary_fields', user_summary_fields)

    common_summary_fields = ("pk", "name")
    summary_fields_serializers = {
        pulpcore_models.Task: common_summary_fields,
        pulp_ansible_models.AnsibleDistribution: common_summary_fields,
        pulp_ansible_models.AnsibleCollectionDeprecated: common_summary_fields,
        pulp_ansible_models.AnsibleNamespaceMetadata: common_summary_fields,
        pulp_ansible_models.Tag: common_summary_fields,
        pulp_ansible_models.AnsibleNamespace: common_summary_fields,
        pulp_ansible_models.CollectionVersionSignature: ("pk", "pubkey_fingerprint"),
        pulp_ansible_models.CollectionVersion: common_summary_fields + ("version",),
        pulp_ansible_models.Collection: common_summary_fields + ("namespace",),
        pulp_ansible_models.CollectionRemote: common_summary_fields,
        pulp_ansible_models.AnsibleRepository: common_summary_fields,
        galaxy_collectionimport_models.CollectionImport: common_summary_fields + ("version",),
        galaxy_namespace_models.NamespaceLink: common_summary_fields,
        galaxy_namespace_models.Namespace: common_summary_fields,
        galaxy_container_models.ContainerDistroReadme: ("pk",),
        galaxy_container_models.ContainerNamespace: common_summary_fields,
        galaxy_container_models.ContainerRegistryRemote: common_summary_fields,
        galaxy_container_models.ContainerRegistryRepos: ("pk",),
        pulp_container_models.ContainerDistribution: common_summary_fields,
        pulp_container_models.ContainerNamespace: common_summary_fields,
        pulp_container_models.ContainerRepository: common_summary_fields,
    }

    def add_summary_fields(obj):
        return {
            field: getattr(obj, field)
            for field in summary_fields_serializers[obj.__class__]
        }

    for model_class in summary_fields_serializers:
        model_class.add_to_class("summary_fields", add_summary_fields)
