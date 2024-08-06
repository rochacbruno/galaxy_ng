import django_filters

from galaxy_ng.app.models.auth import User
from galaxy_ng.app.models.auth import Group
from galaxy_ng.app.models.organization import Organization
from galaxy_ng.app.models.organization import Team


class UserViewFilter(django_filters.FilterSet):
    resource__ansible_id = django_filters.CharFilter(
        field_name="resource__ansible_id", lookup_expr="exact"
    )

    username__contains = django_filters.CharFilter(
        field_name="username", lookup_expr="icontains"
    )

    class Meta:
        model = User
        fields = ["username", "username__contains", "is_superuser", "resource__ansible_id"]


class GroupViewFilter(django_filters.FilterSet):

    class Meta:
        model = Group
        fields = []


class OrganizationFilter(django_filters.FilterSet):
    resource__ansible_id = django_filters.CharFilter(
        field_name="resource__ansible_id", lookup_expr="exact"
    )

    class Meta:
        model = Organization
        fields = ["resource__ansible_id"]


class TeamFilter(django_filters.FilterSet):
    resource__ansible_id = django_filters.CharFilter(
        field_name="resource__ansible_id", lookup_expr="exact"
    )

    class Meta:
        model = Team
        fields = ["resource__ansible_id"]
