# Create a file called custom_auth_backends.py in your app directory

from django.contrib.auth.backends import ModelBackend
from .models import *
from django.db.models import Q


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try to authenticate by username
        user = User.objects.filter(username=username).first()
        if not user:
            # Try to authenticate by email
            user = User.objects.filter(email=username).first()
        if not user:
            # Try to authenticate by phone number
            user = User.objects.filter(phone_number=username).first()

        if user and user.check_password(password):
            return user
        return None