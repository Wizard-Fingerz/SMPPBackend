import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.translation import gettext as _
from django.conf import settings
from .managers import UserManager
from location_field.models.plain import PlainLocationField
from feed.models import Post
from feed.utils import analyze_image, blur_image
import os
from django.conf import settings

# Create your models here.

class ProfileMedia(models.Model):
    media = models.FileField(upload_to='profile_files/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/original/')
    blurred_image = models.ImageField(upload_to='images/blurred/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_sensitive = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.image:
            is_sensitive = analyze_image(self.image.path)
            self.is_sensitive = is_sensitive

            if is_sensitive:
                blurred_path = os.path.join(
                    settings.MEDIA_ROOT, 'blurred_images', os.path.basename(self.image.path)
                )
                blur_image(self.image.path, blurred_path)
                self.blurred_image = os.path.join('blurred_images', os.path.basename(blurred_path))

        super().save(*args, **kwargs)


class CoverImageMedia(models.Model):
    media = models.FileField(upload_to='cover_files/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/original/')
    blurred_image = models.ImageField(upload_to='images/blurred/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_sensitive = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.image:
            is_sensitive = analyze_image(self.image.path)
            self.is_sensitive = is_sensitive

            if is_sensitive:
                blurred_path = os.path.join(
                    settings.MEDIA_ROOT, 'blurred_images', os.path.basename(self.image.path)
                )
                blur_image(self.image.path, blurred_path)
                self.blurred_image = os.path.join('blurred_images', os.path.basename(blurred_path))

        super().save(*args, **kwargs)


class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    is_business = models.BooleanField(
        default=False, verbose_name='Business Account')
    is_personal = models.BooleanField(
        default=False, verbose_name='Personal Account')
    is_admin = models.BooleanField(default=False, verbose_name='Admin Account')
    phone_number = models.BigIntegerField(unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False, verbose_name='Verified')
    last_seen = models.DateTimeField(null=True, blank=True)
    objects = UserManager()
    otp = models.CharField(max_length=5, blank=True)
    otp_verified = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=64)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return str(self.username) or ''


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Rather not say', 'Rather not say'),
)


DAYS_OF_THE_WEEK_CHOICES = (
    ('Sunday', 'Sunday'),
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
)


class BusinessCategory(models.Model):
    name = models.CharField(max_length=250)
    desc = models.TextField()

    def __str__(self):
        return self.name

RELIGION_CHOICES = [
    ('Christianity', 'Christianity'),
    ('Muslim', 'Muslim'),
    ('Indigenous', 'Indigenous'),
    ('Others', 'Others'),
]

class UserProfile(models.Model):
    # Create a one-to-one relationship with the User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    work = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True,)
    gender = models.CharField(
        max_length=15, choices=GENDER_CHOICES, blank=True, null=True)
    custom_gender = models.CharField(max_length=250, blank=True, null=True)
    religion = models.CharField(
        max_length=20, choices=RELIGION_CHOICES, verbose_name='Religion')
    media = models.ForeignKey(ProfileMedia, on_delete=models.CASCADE, blank=True, null=True, related_name='user_media')
    cover_image = models.ForeignKey(CoverImageMedia, on_delete=models.CASCADE, blank=True, null=True, related_name='user_cover_image')
    address = models.ForeignKey('Address', on_delete=models.CASCADE, null=True, related_name='user_address')
    stickers = models.ManyToManyField('self', related_name='sticking', symmetrical=False)
    is_flagged = models.BooleanField(default=False, verbose_name='Flagged')
    favorite_categories = models.ManyToManyField('BusinessCategory', related_name='users_with_favorite', blank=True)
    has_updated_profile = models.BooleanField(default=False)



    def sticker_count(self):
        return self.stickers.count()

    def sticking_count(self):
        return UserProfile.objects.filter(stickers=self.user).count()
    
    def get_recent_hashtags(self):
        # Assuming 'Post' has a 'user' ForeignKey to 'User' and 'hashtag' field
        one_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        recent_posts = Post.objects.filter(user=self.user, timestamp__gte=one_month_ago)
        hashtags = recent_posts.values_list('hashtag', flat=True)
        return list(set(hashtags))  # Return unique hashtags
    
    # @property
    # def date_of_birth(self):
    #     return self._date_of_birth.strftime('%Y-%m-%d')

    # @date_of_birth.setter
    # def date_of_birth(self, value):
    #     self._date_of_birth = datetime.datetime.strptime(value, '%Y-%m-%d').date()
        
    def __str__(self):
        return self.user.username


class Address(models.Model):
    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    current_city = models.CharField(max_length=100, null=True, blank=True)
    street_address = models.CharField(max_length=100, null=True, blank=True)
    apartment_address = models.CharField(max_length=100, null=True, blank=True)
    location = PlainLocationField(based_fields=['current_city'], zoom=7, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ('-created_at', )
    
    def __str__(self):
        components = []
        if self.country:
            components.append(self.country)
        if self.city:
            components.append(self.city)
        if self.street_address:
            components.append(self.street_address)
        if self.apartment_address:
            components.append(self.apartment_address)
        if self.postal_code:
            components.append(self.postal_code)
        return ', '.join(components)



class ReportedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    is_banned = models.BooleanField(default=False, verbose_name='Banned')
    is_disabled = models.BooleanField(default=False, verbose_name='Disabled')

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_received')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_sent')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.recipient.username} from {self.sender.username}: {self.message}"


class BlockedUser(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blockers')
    reason = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked_user}"

    class Meta:
        unique_together = ('blocker', 'blocked_user')