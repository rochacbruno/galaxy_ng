# from django.contrib.auth.models import User
from rest_framework import serializers

from galaxy_ng.app.api.ui.serializers import UserSerializer as UserSerializerV1
from galaxy_ng.app.models.auth import User
from galaxy_ng.app.models.auth import Group
from galaxy_ng.app.models.organization import Organization
from galaxy_ng.app.models.organization import Team


class UserSerializer(UserSerializerV1):
    resource = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'groups',
            'date_joined',
            'is_superuser',
            'auth_provider',
            'resource',
        ]

    def get_resource(self, obj):
        return obj.resource.summary_fields()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id',
            'name',
        ]


class OrganizationSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    resource = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id',
            'name',
            'resource',
        ]

    def get_id(self, obj):
        return obj.pk

    def get_resource(self, obj):
        return {
            'resource_type': obj.resource.content_type.name,
            'ansible_id': obj.resource.ansible_id,
        }


class TeamSerializer(serializers.ModelSerializer):

    group = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    resource = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'group',
            'organization',
            'resource',
        ]

    def get_group(self, obj):
        return {
            'id': obj.group.id,
            'name': obj.group.name,
        }

    def get_organization(self, obj):
        return {
            'id': obj.organization.id,
            'name': obj.organization.name,
        }

    def get_resource(self, obj):
        return {
            'resource_type': obj.resource.content_type.name,
            'ansible_id': obj.resource.ansible_id,
        }
