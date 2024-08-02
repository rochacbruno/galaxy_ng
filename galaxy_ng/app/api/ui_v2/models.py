from django.db import models
from django.contrib.auth import get_user_model
from ansible_base.resource_registry.models import Resource
from galaxy_ng.app.models import Organization
from galaxy_ng.app.models import Team
from galaxy_ng.app.models import Group

User = get_user_model()


class OrganizationResourcesView(models.Model):

    organization = models.ForeignKey(
        Organization,
        to_field='id',
        db_column='org_id',
        on_delete=models.DO_NOTHING,
        primary_key=True
    )
    resource = models.ForeignKey(
        Resource,
        to_field='id',
        db_column='resource_id',
        on_delete=models.DO_NOTHING
    )

    class Meta:
        managed = False
        db_table = 'galaxy_dab_organization_resources_view'


class TeamResourcesView(models.Model):

    team = models.ForeignKey(
        Team,
        to_field='id',
        db_column='team_id',
        on_delete=models.DO_NOTHING,
        primary_key=True
    )
    group = models.ForeignKey(
        Group,
        to_field='id',
        db_column='group_id',
        on_delete=models.DO_NOTHING
    )
    organization = models.ForeignKey(
        Organization,
        to_field='id',
        db_column='organization_id',
        on_delete=models.DO_NOTHING
    )
    resource = models.ForeignKey(
        Resource,
        to_field='id',
        db_column='resource_id',
        on_delete=models.DO_NOTHING
    )

    class Meta:
        managed = False
        db_table = 'galaxy_dab_team_resources_view'
