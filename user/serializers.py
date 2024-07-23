from rest_framework import serializers
from .models import *
from django.db.models import Q
from rest_framework import serializers
from django.db.models import Q
from django.utils.translation import gettext as _
from django.contrib.auth.hashers import check_password


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'



class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)  # Make phone_number optional
    email = serializers.EmailField(required=False, allow_blank=True)  # Make email optional
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'username', 'password']

    def validate(self, validated_data):
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')

        if not email and not phone_number:
            raise serializers.ValidationError("Enter an email or a phone number.")

        return validated_data

    def create(self, validated_data):
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')
        username = email if email else phone_number  # Set username to email or phone_number

        # Debugging statement: Print the email and phone number
        print(f"Creating user with Email: {email}, Phone Number: {phone_number}")

        # Create and save the User instance
        user = User.objects.create_user(
            username=username,
            email=email,
            phone_number=phone_number,
            password=validated_data.get('password'),
        )

        return user


class ReportUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedUser
        fields = ['user', 'description']


class ReportedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedUser
        fields = '__all__'


class BusinessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCategory
        fields = ['name',]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class CurrentCityAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address  # Replace 'Address' with the actual name of your Address model
        fields = ('current_city',)


class UserProfileSerializer(serializers.ModelSerializer):
    stickers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    sticking = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    stickers_count = serializers.SerializerMethodField()
    sticking_count = serializers.SerializerMethodField()
    address = CurrentCityAddressSerializer()
    recent_hashtags = serializers.SerializerMethodField()


    class Meta:
        model = UserProfile
        fields = ('work', 'date_of_birth', 'gender', 'custom_gender', 'address',
                  'stickers', 'sticking', 'stickers_count', 'sticking_count', 'recent_hashtags')

    def get_stickers_count(self, obj):
        return obj.sticker_count()

    def get_sticking_count(self, obj):
        return obj.sticking_count()
    
    def get_recent_hashtags(self, obj):
        return obj.get_recent_hashtags()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'profile')

    extra_kwargs = {
        # Password field should be write-only
        'password': {'write_only': True},
    }

    def update(self, instance, validated_data):
        # Update User fields
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        # Update UserProfile fields
        profile_data = validated_data.get('profile', {})
        profile = instance.profile

        profile.work = profile_data.get('work', profile.work)
        profile.date_of_birth = profile_data.get(
            'date_of_birth', profile.date_of_birth)
        profile.gender = profile_data.get('gender', profile.gender)
        profile.custom_gender = profile_data.get(
            'custom_gender', profile.custom_gender)

        # Update Address fields (including current city)
        address_data = profile_data.get('address', {})
        address = profile.address

        address.current_city = address_data.get(
            'current_city', address.current_city)

        # Save both User, UserProfile, and Address instances
        instance.save()
        profile.save()
        address.save()

        return instance


class UserListSerializer(serializers.ModelSerializer):
    sticking_count = serializers.SerializerMethodField()
    sticker_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'sticking_count', 'sticker_count')

    def get_sticking_count(self, obj):
        try:
            user_profile = UserProfile.objects.get(user=obj)
            return user_profile.sticking.count()
        except UserProfile.DoesNotExist:
            return 0

    def get_sticker_count(self, obj):
        try:
            user_profile = UserProfile.objects.get(user=obj)
            return user_profile.stickers.count()
        except UserProfile.DoesNotExist:
            return 0


class UserDeletionSerializer(serializers.Serializer):
    reason_choice = serializers.CharField(write_only=True, required=False)
    reason = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class BlockedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedUser
        fields = ('blocker', 'blocked_user', 'reason')

class BusinessAccountLoginSerializer(serializers.Serializer):
    business_name = serializers.CharField()
    business_password = serializers.CharField()


class GeneralSearchSerializer(serializers.Serializer):
    query = serializers.CharField()


class FlagUserProfileSerializer(serializers.Serializer):
    username = serializers.CharField()



class CheckProfileUpdateStatus(serializers.Serializer):
    class Meta:
        model = UserProfile
        fields = ('has_updated_profile',)


class UserSerializer2(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileMedia
        fields = '__all__'


class CoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverImageMedia
        fields = '__all__'


class UserProfileSerializer2(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(format='%Y-%m-%d')
    user = UserSerializer2()
    profile_image = ProfileMediaSerializer(
        required=False)  # Add required=False here
    cover_image = ProfileMediaSerializer(
        required=False)  # Add required=False here

    class Meta:
        model = UserProfile
        fields = ['user', 'work', 'date_of_birth', 'gender',
                  'custom_gender', 'religion', 'cover_image', 'profile_image']

class UserProfileSerializerMain(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['work', 'date_of_birth', 'gender', 'custom_gender', 'religion', 'media', 'cover_image', 'address', 'is_flagged', 'favorite_categories', 'has_updated_profile', 'sticker_count', 'sticking_count']

class UserSerializerMain(serializers.ModelSerializer):
    profile = UserProfileSerializerMain(source='userprofile', read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_business', 'is_personal', 'phone_number', 'is_verified', 'last_seen', 'profile']

