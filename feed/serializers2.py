
# serializers.py
from rest_framework import serializers
from .models import Post, PostMedia
from user.models import User

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Include fields as needed

