from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):

        print("Migrating role definitions for DAB ...")

        from django.contrib.auth.models import Permission
        # from django.contrib.contenttypes.models import ContentType
        from ansible_base.rbac.models import RoleDefinition
        from ansible_base.rbac.models import DABPermission

        from galaxy_ng.app.access_control.statements.standalone import STANDALONE_STATEMENTS
        from galaxy_ng.app.access_control.statements.roles import LOCKED_ROLES

        # The UI code is the only place I could find the descriptions for the roles ...
        # https://github.com/ansible/ansible-hub-ui/blob/364d9af2d80d2defecfab67f44706798b8d2cf83/src/utilities/translate-locked-role.ts#L9
        galaxy_role_description = {
            'core.task_owner': 'Allow all actions on a task.',
            'core.taskschedule_owner': 'Allow all actions on a task schedule.',
            'galaxy.ansible_repository_owner': 'Manage ansible repositories.',
            'galaxy.collection_admin': (
                'Create, delete and change collection namespaces. '
                + 'Upload and delete collections. Sync collections from remotes.'
                + ' Approve and reject collections.'
            ),
            'galaxy.collection_curator': 'Approve, reject and sync collections from remotes.',
            'galaxy.collection_namespace_owner': 'Change and upload collections to namespaces.',
            'galaxy.collection_publisher': 'Upload and modify collections.',
            'galaxy.collection_remote_owner': 'Manage collection remotes.',
            'galaxy.content_admin': 'Manage all content types.',
            'galaxy.execution_environment_admin': (
                'Push, delete and change execution environments.'
                + ' Create, delete and change remote registries.'
            ),
            'galaxy.execution_environment_collaborator': 'Change existing execution environments.',
            'galaxy.execution_environment_namespace_owner':
                'Create and update execution environments under existing container namespaces.',
            'galaxy.execution_environment_publisher': 'Push and change execution environments.',
            'galaxy.group_admin': 'View, add, remove and change groups.',
            'galaxy.synclist_owner': 'View, add, remove and change synclists.',
            'galaxy.task_admin': 'View and cancel any task.',
            'galaxy.user_admin': 'View, add, remove and change users.',
        }

        # make a list of model_or_obj perms that galaxy actually cares about ...
        galaxy_model_perms = set()
        for statement_group, action_items in STANDALONE_STATEMENTS.items():
            for action_item in action_items:
                if 'condition' not in action_item:
                    continue
                if isinstance(action_item['condition'], list):
                    conditions = action_item['condition']
                else:
                    conditions = [action_item['condition']]
                for condition in conditions:
                    if not condition.startswith('has_model_'):
                        continue
                    galaxy_model_perms.add(condition.split(':', 1)[1])

        # include permissions from the LOCKED_ROLES struct ...
        for role_name, permissions in LOCKED_ROLES.items():
            for perm in permissions['permissions']:
                galaxy_model_perms.add(perm)

        # make an index of all current dab permissions ...
        dabperm_map = {}
        for dabperm in DABPermission.objects.all():
            perm_codename = dabperm.codename
            ctype_model = dabperm.content_type.model
            app_label = dabperm.content_type.app_label
            dabperm_map[(app_label, ctype_model, perm_codename)] = dabperm

        # For every permission in the system that galaxy cares about, make a dabpermission
        for perm in Permission.objects.all():

            # skip if not in the list of things galaxy cares about ...
            gkey = f'{perm.content_type.app_label}.{perm.codename}'
            if gkey not in galaxy_model_perms:
                continue

            # model = perm.content_type.model
            dkey = (perm.content_type.app_label, perm.content_type.model, perm.codename)
            if dkey in dabperm_map:
                dabperm = dabperm_map[dkey]
            else:
                print(f'creating perm {dkey} ..')
                dabperm = DABPermission.objects.create(
                    codename=perm.codename,
                    content_type=perm.content_type,
                    name=perm.name
                )
                dabperm_map[dkey] = dabperm

        # copy all of the galaxy roles to dab roledefinitions ...
        for role_name, permissions in LOCKED_ROLES.items():
            role_description = galaxy_role_description.get(role_name, '')
            print(f'{role_name} ... {role_description}')

            # find the related permissions based on app name and permission name ...
            related_perms = []
            for pcode in permissions['permissions']:
                pcode_parts = pcode.split('.')
                app_name = pcode_parts[0]
                perm_name = pcode_parts[1]

                for k, v in dabperm_map.items():
                    if k[0] == app_name and k[2] == perm_name:
                        related_perms.append(v)
                        break

            # we need ALL of the necessary permissions ...
            assert len(related_perms) == \
                len(permissions['permissions']), f"didn't find all the permissions for {role_name}"

            # get or make the def ...
            rd, created = RoleDefinition.objects.get_or_create(name=role_name)
            if created:
                print('\tcreated')

            # set the description for the UI ...
            rd.description = role_description

            # add each related permission ...
            for rperm in related_perms:
                if not rd.permissions.filter(id=rperm.id).exists():
                    print(f'\tadd {rperm}')
                    rd.permissions.add(rperm)

            # what are all the content types involved ... ?
            ctypes = []
            for permission_name in permissions['permissions']:
                app_label = permission_name.split('.', 1)[0]
                perm_name = permission_name.split('.', 1)[1]
                try:
                    perm = Permission.objects.get(
                        codename=perm_name,
                        content_type__app_label=app_label
                    )
                except Exception as e:
                    # print(e)
                    # import epdb; epdb.st()
                    raise e
                ctypes.append((perm.content_type_id, perm.content_type))

            ctypes = sorted(set(ctypes))
            if len(ctypes) == 1:
                if rd.content_type_id != ctypes[0][1]:
                    print(f'\tsetting {role_name} content type to {ctypes[0][1]}')
                    rd.content_type_id = ctypes[0][1]
                    rd.content_type = ctypes[0][1]

            rd.save()
