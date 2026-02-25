from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with either
    their username or email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by username or email
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Multiple users with same email - fall back to username only
            user = User.objects.filter(username=username).first()
            if user is None:
                return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
