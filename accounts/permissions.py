from functools import wraps

from django.core.exceptions import PermissionDenied


ADMIN_GROUP = "EduFee Admin"
ACCOUNTS_GROUP = "Accounts Staff"
STUDENT_GROUP = "Student"


def is_admin(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name=ADMIN_GROUP).exists()
        )
    )


def is_accounts_staff(user):
    return (
        user.is_authenticated
        and (
            is_admin(user)
            or user.groups.filter(name=ACCOUNTS_GROUP).exists()
        )
    )


def is_student(user):
    return (
        user.is_authenticated
        and user.groups.filter(name=STUDENT_GROUP).exists()
    )


def role_required(role_checker):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                raise PermissionDenied

            if not role_checker(request.user):
                raise PermissionDenied

            return view_func(
                request,
                *args,
                **kwargs,
            )

        return wrapper

    return decorator