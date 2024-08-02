from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0053_wait_for_dab_rbac'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE VIEW galaxy_dab_organization_resources_view AS
            SELECT
                o.id AS org_id,
                r.id AS resource_id
            FROM galaxy_organization o
            LEFT JOIN dab_resource_registry_resource r ON r.object_id = o.id::text
            WHERE r.content_type_id = (SELECT id FROM django_content_type WHERE app_label = 'galaxy' AND model = 'organization');
            """,
            reverse_sql="DROP VIEW IF EXISTS galaxy_dab_organization_resources_view;"
        ),
        migrations.RunSQL(
            """
            CREATE VIEW galaxy_dab_team_resources_view AS
            SELECT
                t.id AS team_id,
                t.organization_id AS organization_id,
                t.group_id AS group_id,
                r.id AS resource_id
            FROM galaxy_team t
            LEFT JOIN dab_resource_registry_resource r ON r.object_id = t.id::text
            WHERE r.content_type_id = (SELECT id FROM django_content_type WHERE app_label = 'galaxy' AND model = 'team');
            """,
            reverse_sql="DROP VIEW IF EXISTS galaxy_dab_team_resources_view;"
        ),
    ]
