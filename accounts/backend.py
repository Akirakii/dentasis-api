from django.contrib.auth.backends import ModelBackend
from .models import User

__all__ = ["AuthenticationBackend"]


class AuthenticationBackend(ModelBackend):
    """
    Returns the user even if the user is inactive.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None:
            email = kwargs.get(User.email)
        if email is None or password is None:
            return
        try:
            user = User._default_manager.get_by_natural_key(email)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.check_password(password):
                return user
