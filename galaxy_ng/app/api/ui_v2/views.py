from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse

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


class OrganizationViewSet(viewsets.ModelViewSet):
    # queryset = OrganizationResourcesView.objects.all().order_by('organization__id')
    queryset = Organization.objects.all().order_by('pk')
    serializer_class = OrganizationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrganizationFilter
    pagination_class = DefaultPaginator


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('id')
    serializer_class = TeamSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TeamFilter
    pagination_class = DefaultPaginator
