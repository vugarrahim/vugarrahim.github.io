import json
from django.conf import settings
from django.contrib.auth.models import Group, Permission


def sync_permissions():
    groups, permssions = '%s/accounts/boost/json/groups.json' % settings.BASE_DIR, '%s/accounts/boost/json/permissions.json' % settings.BASE_DIR
    with open(groups) as group_file:
        with open(permssions) as permission_file:
            groups_json = json.load(group_file)
            permissions_json = json.load(permission_file)
            create_groups(groups=groups_json, permissions=permissions_json)




def create_groups(groups, permissions):
    for group in groups:
        print(group)

        role, created = Group.objects.get_or_create(name=group['fields']['name'])
        for perm_id in group['fields']['permissions']:
            # codename = get_perm_by_id(id=perm_id, permissions=permissions)['fields']['codename']
            # role.permissions.add(Permission.objects.get(codename=codename))
            role.permissions.add(Permission.objects.get(id=perm_id))

        role.save()





def get_perm_by_id(id, permissions):
    for permission in permissions:
        if id == permission["pk"]:
            return permission