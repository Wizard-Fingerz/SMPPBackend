from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    def _create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        if not email and not phone_number:
            raise ValueError("Either email or phone number must be provided.")
        
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_personal', True)
        return self._create_user(email=email, phone_number=phone_number, password=password, **extra_fields)
    
    
    def create_business_user(self, email=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_business', True)
        extra_fields.setdefault('is_personal', False)
        return self._create_user(email=email, phone_number=phone_number, password=password, **extra_fields)
    
    def create_superuser(self, email=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_verified', True)

        if not email and not phone_number:
            raise ValueError("Either email or phone number must be provided.")
        
        return self._create_user(email=email, phone_number=phone_number, password=password, **extra_fields)
