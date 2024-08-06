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
        from pulp_container.app.models import ContainerNamespace, ContainerRepository
        from pulpcore.app.models.task import Task
        from ansible_base.rbac import permission_registry

        permission_registry.register(ContainerNamespace, ContainerRepository, Task, parent_field_name=None)
