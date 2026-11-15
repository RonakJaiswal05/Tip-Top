import getpass
import os

from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from core.roles import ROLES


class Command(BaseCommand):
    help = "Create a staff account with a role. Owner and Manager set up the authenticator app at first sign-in."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--role", required=True, choices=ROLES)
        parser.add_argument("--email", default="")
        parser.add_argument("--first-name", default="")
        parser.add_argument("--last-name", default="")
        parser.add_argument("--password-env", help="Read the password from this environment variable instead of asking.")

    def handle(self, *args, **o):
        if User.objects.filter(username=o["username"]).exists():
            raise CommandError("This username exists already.")
        pw = os.environ.get(o["password_env"]) if o.get("password_env") else None
        if not pw:
            pw = getpass.getpass("Password: ")
            if pw != getpass.getpass("Password (again): "):
                raise CommandError("Passwords do not match.")
        u = User(username=o["username"], email=o["email"], first_name=o["first_name"], last_name=o["last_name"], is_staff=True)
        try:
            validate_password(pw, u)
        except ValidationError as e:
            raise CommandError(" ".join(e.messages))
        u.set_password(pw)
        u.save()
        u.groups.add(Group.objects.get_or_create(name=o["role"])[0])
        self.stdout.write(self.style.SUCCESS(f"Created {u.username} ({o['role']})."))
