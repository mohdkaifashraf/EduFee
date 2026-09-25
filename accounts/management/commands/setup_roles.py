from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Create and configure EduFee user roles."

    def handle(self, *args, **options):

        roles = {
            "EduFee Admin": [
                "add_student",
                "change_student",
                "delete_student",
                "view_student",
                "view_all_students",
            ],
            "Accounts Staff": [
                "add_student",
                "change_student",
                "view_student",
                "view_all_students",
            ],
            "Student": [
                "view_student",
            ],
        }

        for role_name, permission_codenames in roles.items():

            group, created = Group.objects.get_or_create(
                name=role_name
            )

            permissions = Permission.objects.filter(
                content_type__app_label="students",
                codename__in=permission_codenames,
            )

            group.permissions.set(permissions)

            action = "Created" if created else "Updated"

            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} role: {role_name}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "EduFee roles configured successfully."
            )
        )