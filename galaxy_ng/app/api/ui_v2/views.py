from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import MethodNotAllowed

from ansible_base.rest_pagination.default_paginator import DefaultPaginator

from .filters import UserViewFilter
from .filters import GroupViewFilter
from .filters import OrganizationFilter
from .filters import TeamFilter
from .serializers import UserSerializer
from .serializers import GroupSerializer
from .serializers import OrganizationSerializer
from .serializers import TeamSerializer

from galaxy_ng.app.models.auth import User
from galaxy_ng.app.models.auth import Group
from galaxy_ng.app.models.organization import Organization
from galaxy_ng.app.models.organization import Team


def version_view(request):
    data = {
        "version": "2024-08-05T18:00:00"
    }
    return JsonResponse(data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserViewFilter
    pagination_class = DefaultPaginator


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('id')
    serializer_class = GroupSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupViewFilter
    pagination_class = DefaultPaginator

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def get_permissions(self):
        if self.action == 'create':
            raise MethodNotAllowed('POST')
        return super().get_permissions()


class OrganizationViewSet(viewsets.ModelViewSet):

    queryset = Organization.objects.all().order_by('pk')
    serializer_class = OrganizationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrganizationFilter
    pagination_class = DefaultPaginator

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.name == "Default" and request.data.get('name') != "Default":
            raise ValidationError("The name 'Default' cannot be changed.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.name == "Default":
            raise ValidationError("'Default' organization cannot be deleted.")

        return super().destroy(request, *args, **kwargs)


class TeamViewSet(viewsets.ModelViewSet):

    queryset = Team.objects.all().order_by('id')
    serializer_class = TeamSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TeamFilter
    pagination_class = DefaultPaginator

    def create(self, request, *args, **kwargs):

        # make the organization ...
        org_name = request.data.get('organization', 'Default')
        organization, _ = Organization.objects.get_or_create(
            name=org_name
        )

        # make the team ...
        team, created = Team.objects.get_or_create(
            name=request.data['name'],
            defaults={'organization': organization}
        )
        if not created:
            raise ValidationError("A team with this name already exists.")

        # set the group name ...
        group_name = organization.name + '::' + team.name
        team.group.name = group_name
        team.group.save()

        serializer = self.serializer_class(team)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
