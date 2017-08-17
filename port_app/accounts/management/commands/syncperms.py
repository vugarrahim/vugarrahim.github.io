from django.core.management.base import CommandError, BaseCommand
from accounts.boost.db_auto import sync_permissions


class Command(BaseCommand):
    help = "Looks for the permissions on the file json/permissions.josn, and adds them to the groups"

    def handle(self, *args, **options):
        print('--- Syncs permissions')
        sync_permissions()
        print('--- Synchronization completed')
