from django.db import models
from user.models import *
from django.db import models
from django.contrib.auth.models import User
from .utils import analyze_image, blur_image
from PIL import Image as PilImage, ImageFilter
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Create your models here.

import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

class PostMedia(models.Model):
    post = models.ForeignKey('Post', related_name='media', on_delete=models.CASCADE)
    file = models.FileField(upload_to='post_files/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blurred_image = models.ImageField(upload_to='blurred_images/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_sensitive = models.BooleanField(default=False)
    user_sensitive = models.BooleanField(default=False)
    sensitivity = models.CharField(max_length=10, default='low')

    def save(self, *args, **kwargs):
        if self.file:
            file_name = self.file.name
            file_path = os.path.join(settings.MEDIA_ROOT, 'post_files', file_name)

            # Save the in-memory file to disk
            if not os.path.exists(file_path):
                path = default_storage.save(file_path, ContentFile(self.file.read()))

            # Determine if the image should be blurred based on sensitivity settings
            self.user_sensitive = self.sensitivity == 'high'
            if not self.user_sensitive:
                is_sensitive = analyze_image(file_path)
                self.is_sensitive = is_sensitive
            else:
                self.is_sensitive = True

            # Handle image blurring if needed
            if self.is_sensitive:
                blurred_images_dir = os.path.join(settings.MEDIA_ROOT, 'blurred_images')
                if not os.path.exists(blurred_images_dir):
                    os.makedirs(blurred_images_dir)

                blurred_path = os.path.join(
                    blurred_images_dir, os.path.basename(file_path)
                )
                try:
                    blur_image(file_path, blurred_path)
                    self.blurred_image = os.path.join('blurred_images', os.path.basename(blurred_path))
                except Exception as e:
                    print(f"Error blurring image: {e}")

        super().save(*args, **kwargs)

                
class CommentMedia(models.Model):
    media = models.FileField(upload_to='comment_files/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/original/')
    blurred_image = models.ImageField(upload_to='images/blurred/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_sensitive = models.BooleanField(default=False)


class PromotionPlan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in days")

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.URLField(blank=True, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reaction = models.ForeignKey(
        'Reaction', on_delete=models.SET_NULL, null=True, blank=True)
    comments = models.ForeignKey(
        'Comment', on_delete=models.SET_NULL, null=True, related_name='post_comments')
    hashtag = models.CharField(max_length=250, blank=True)
    is_business_post = models.BooleanField(
        default=False, verbose_name='Business Post')
    is_personal_post = models.BooleanField(
        default=True, verbose_name='Personal Post')
    tagged_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='tagged_in_posts', blank=True)
    # Add a reverse relationship for media
    def get_media(self):
        return PostMedia.objects.filter(post=self)


class SharePost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    caption = models.TextField(blank=True, null=True)
    shared_post = models.ForeignKey('Post', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    content = models.TextField()
    media = models.ForeignKey(CommentMedia, on_delete=models.CASCADE, blank= True, null= True)
    reaction = models.ForeignKey(
        'Reaction', on_delete=models.SET_NULL, null=True)
    timestamp = models.TimeField()


class Reply(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    content = models.TextField()
    reaction = models.ForeignKey(
        'Reaction', on_delete=models.SET_NULL, null=True)


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('love', 'Love'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('others', 'Others'),
    ]

    reaction_type = models.CharField(
        max_length=20, choices=REACTION_CHOICES, verbose_name='Reaction')


class Repost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    timestamp = models.TimeField()
    reaction = models.ForeignKey(
        'Reaction', on_delete=models.SET_NULL, null=True)
    comments = models.ForeignKey(
        'Comment', on_delete=models.SET_NULL, null=True)


class SavedPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    timestamp = models.TimeField()


class PromotedPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    promotion_plan = models.ForeignKey(PromotionPlan, on_delete=models.CASCADE)
    promotion_status = models.CharField(max_length=20, choices=[(
        'pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)



class AdvertCategory(models.Model):
    name = models.CharField(max_length=250, blank=True, null= True)

class Advert(models.Model):
    
    DURATION_CHOICES = [
        ('24hrs', '24HRS'),
    ]
    title = models.CharField(max_length=250, blank=True, null=True)
    category = models.ForeignKey(AdvertCategory, on_delete=models.CASCADE)
    duration = models.CharField(max_length=250, choices=DURATION_CHOICES)
    custom_duration_start = models.DateTimeField()
    custom_duration_end = models.DateTimeField()
    