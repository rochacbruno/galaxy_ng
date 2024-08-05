from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse

from ansible_base.rest_pagination.default_paginator import DefaultPaginator

from .filters import UserViewFilter
from .filters import GroupViewFilter
from .filters import OrganizationResourcesViewFilter
from .filters import TeamResourcesViewFilter
from .models import OrganizationResourcesView
from .models import TeamResourcesView
from .serializers import UserSerializer
from .serializers import GroupSerializer
from .serializers import OrganizationSerializer
from .serializers import TeamSerializer

from galaxy_ng.app.models.auth import User
from galaxy_ng.app.models.auth import Group


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
    queryset = OrganizationResourcesView.objects.all().order_by('organization__id')
    serializer_class = OrganizationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrganizationResourcesViewFilter
    pagination_class = DefaultPaginator


class TeamViewSet(viewsets.ModelViewSet):
    queryset = TeamResourcesView.objects.all().order_by('team__id')
    serializer_class = TeamSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TeamResourcesViewFilter
    pagination_class = DefaultPaginator
