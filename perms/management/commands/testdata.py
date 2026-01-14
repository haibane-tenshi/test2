from django.core.management.base import BaseCommand
from perms.models import User
from perms.secure import context as secure_context


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        alice = User.objects.create(
            name="alice",
            passhash=secure_context.hash("alice"),
            is_admin=False,
            is_active=True,
        )
        alice.userpermission_set.create(url="test/a")

        bob = User.objects.create(
            name="bob",
            passhash=secure_context.hash("bob"),
            is_admin=False,
            is_active=True,
        )
        bob.userpermission_set.create(url="test/b")

        charlie = User.objects.create(
            name="charlie",
            passhash=secure_context.hash("charlie"),
            is_admin=False,
            is_active=True,
        )
        charlie.userpermission_set.create(url="test/b")

        admin = User.objects.create(
            name="admin",
            passhash=secure_context.hash("admin"),
            is_admin=True,
            is_active=True,
        )
