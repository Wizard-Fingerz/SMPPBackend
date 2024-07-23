from django.shortcuts import render
from ctypes import pointer
import json  # Add this import for JSON formatting
import time  # Import the time module
from django.db.models import *
from django.db.models import Q
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework.authentication import *
from rest_framework.viewsets import GenericViewSet
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from feed.models import *
from .serializers import *
from django.middleware import csrf
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import authentication_classes, permission_classes
from django.contrib.auth import authenticate, login
from .authentication_backends import *
from rest_framework.views import *
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import status, permissions
from rest_framework import generics, filters, viewsets
from rest_framework.generics import *
import pyotp
import secrets
import base64
import logging


# Configure logging
logger = logging.getLogger(__name__)

# Create your views here.
def generate_otp_code(secret_key, length=5):
    totp = pyotp.TOTP(secret_key, digits=length)  # Set the digits parameter
    otp_code = totp.now()

    # Log the secret key and OTP code for debugging
    logger.debug(f"Secret Key: {secret_key}")
    logger.debug(f"OTP Code: {otp_code}")

    return otp_code



from rest_framework.parsers import JSONParser

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def create_user(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)

        print(f"Request Data: {data}")

        email = data.get('email')
        phone_number = data.get('phone_number')

        print(f"Email: {email}, Phone Number: {phone_number}")

        if not email and not phone_number:
            return Response({'error': 'Either email or phone number must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Set username based on the provided email or phone number
        username = email if email else phone_number
        data['username'] = username

        serializer = UserRegistrationSerializer(data=data, context={'request': request})

        if email:
            if User.objects.filter(email=email).exists():
                return Response({'error': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        elif phone_number:
            if User.objects.filter(phone_number=phone_number).exists():
                return Response({'error': 'User with this phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            try:
                user = serializer.save()

                secret_key = base64.b32encode(secrets.token_bytes(10)).decode('utf-8')
                user.secret_key = secret_key
                user.save()

                token, created = Token.objects.get_or_create(user=user)
                token_key = token.key

                otp_code = generate_otp_code(user.secret_key)

                user.otp = otp_code
                user.save()
                
                response_data = serializer.data
                response_data['token'] = token_key
                return Response(response_data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                print(e)
                return Response({'error': 'Account details already exist.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Both username and password are required.'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in and return a success response
            login(request, user)
            return JsonResponse({'message': 'Login successful', 'token': user.auth_token.key})
        else:
            # Authentication failed; return an error response
            return JsonResponse({'error': 'Invalid login credentials'}, status=401)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Get the user's token
    user = request.user
    try:
        token = Token.objects.get(user=user)
        token.delete()  # Delete the token
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({'error': 'No token found for the user.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user

    if request.method == 'PUT':
        serializer = UserProfileUpdateSerializer(
            instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User profile updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileHasUpdatedProfileView(generics.GenericAPIView):
    serializer_class = UserProfileSerializer
    # permission_classes = [AllowAny]
    # authentication_classes = [TokenAuthentication]

    def get_object(self):
        # Retrieve the user's profile based on the authenticated user
        user = self.request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    # Validate the request data using the serializer
    serializer = UserDeletionSerializer(data=request.data)
    if serializer.is_valid():
        # Authenticate the user based on the provided password
        user = authenticate(username=request.user.username,
                            password=serializer.validated_data['password'])
        if user is not None:
            # Logout the user to invalidate the current session
            request.auth.logout(request)

            # Delete the user
            user.delete()

            return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user_by_username_or_id(request):
    # Validate the request data using the serializer
    serializer = UserDeletionSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        user_id = serializer.validated_data.get('user_id')

        if username:
            try:
                user = User.objects.get(username=username)
                user.delete()
                return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except User.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        elif user_id:
            try:
                user = User.objects.get(pk=user_id)
                user.delete()
                return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except User.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Provide either 'username' or 'user_id' for deletion"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def delete_account_by_username(request, username):
    # Attempt to get the user by username
    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        # Check if the request is a POST request to confirm the deletion
        user.delete()
        return JsonResponse({"message": "User deleted successfully."}, status=204)

    # If it's not a POST request, return a message indicating how to delete the user
    return JsonResponse(
        {"message": "To delete this user, send a POST request to this endpoint."},
        status=400
    )


def delete_account_by_id(request, user_id):
    # Attempt to get the user by their ID
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        # Check if the request is a POST request to confirm the deletion
        user.delete()
        return JsonResponse({"message": "User deleted successfully."}, status=204)

    # If it's not a POST request, return a message indicating how to delete the user
    return JsonResponse(
        {"message": "To delete this user, send a POST request to this endpoint."},
        status=400
    )


# End of Authentication APIs

class UserDetailsView(APIView):
    def get(self, request):
        user = request.user
        data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        try:
            profile = user.profile  # Assuming user has a related Profile object
            data['profile'] = {
                'bio': profile.bio,
                'location': profile.location,
                'birth_date': profile.birth_date,
                'media': profile.media
            }
            data['profile']['recent_hashtags'] = profile.get_recent_hashtags()
        except UserProfile.DoesNotExist:
            data['profile'] = {
                'bio': '',
                'location': '',
                'birth_date': None,
                'recent_hashtags': []
            }
        except AttributeError:
            data['profile'] = {
                'bio': '',
                'location': '',
                'birth_date': None,
                'recent_hashtags': []
            }

        return Response(data, status=status.HTTP_200_OK)
    
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        location_data = request.data.get('location')
        if location_data:
            # Assuming location_data is a dictionary with 'latitude' and 'longitude' keys
            latitude = location_data.get('latitude')
            longitude = location_data.get('longitude')

            # Create or update user location
            user = self.perform_create(serializer)
            # Create a Point object from coordinates
            user.location = pointer(longitude, latitude)
            user.save()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserAPIView(RetrieveAPIView):
    """
    Get user details
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user



class UserSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')

        if query:
            # Perform a case-insensitive search across relevant fields in the database
            results = User.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(username__icontains=query)
            )
            serializer = UserSerializer(results, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)


# Report Users API

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def report_user(request):
    if request.method == 'POST':
        serializer = ReportUserSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            report = serializer.save()
            response_data = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Report not successful'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_user(request):
    # Get the user who is doing the blocking
    blocker = request.user

    # Get the user who is being blocked (you can pass this user's ID or username in the request data)
    blocked_user_id = request.data.get('blocked_user_id')

    # Check if the block already exists
    existing_block = BlockedUser.objects.filter(
        blocker=blocker, blocked_user__id=blocked_user_id).first()

    if existing_block:
        return Response({'detail': 'User is already blocked.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new block
    serializer = BlockedUserSerializer(
        data={'blocker': blocker.id, 'blocked_user': blocked_user_id})
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'User blocked successfully.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_blocked_users(request):
    # Get the authenticated user
    user = request.user

    # Retrieve the list of users they have blocked
    blocked_users = BlockedUser.objects.filter(blocker=user)

    # Serialize the blocked users data
    serializer = BlockedUserSerializer(blocked_users, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)



class ReportUserViewSet(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = ReportedUser.objects.all()
    serializer_class = ReportedUserSerializer
    lookup_field = 'user_id'

# End of report users
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from datetime import datetime

class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer2

    def get_object(self):
        user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return user_profile

    def perform_update(self, serializer):
        print('perform_update started')
        user_profile = self.get_object()
        print(f'Got user profile: {user_profile.user.email}')

        print("Received Data:")
        print(self.request.data)

        # Update the first name and last name fields
        user_data = self.request.data.get('user', {})
        user_profile.user.first_name = self.request.data.get('user.first_name', user_profile.user.first_name)
        user_profile.user.last_name = self.request.data.get('user.last_name', user_profile.user.last_name)
        user_profile.work = self.request.data.get('work', user_profile.work)
        user_profile.gender = self.request.data.get('gender', user_profile.gender)
        user_profile.religion = self.request.data.get('religion', user_profile.religion)
        user_profile.custom_gender = self.request.data.get('custom_gender', user_profile.custom_gender)
        date_of_birth = self.request.data.get('date_of_birth', None)
        profile_image_data = self.request.FILES.get('profile_image')
        cover_image_data = self.request.FILES.get('cover_image')

        if profile_image_data:
            if user_profile.media:
                user_profile.media.media = profile_image_data
            else:
                profile_media = ProfileMedia(media=profile_image_data, user=user_profile.user)
                profile_media.save()
                user_profile.media = profile_media

        if cover_image_data:
            if user_profile.cover_image:
                user_profile.cover_image.media = cover_image_data
            else:
                cover_image_media = CoverImageMedia(media=cover_image_data, user=user_profile.user)
                cover_image_media.save()
                user_profile.cover_image = cover_image_media

        print("Profile Data to Save:")
        print(f"first_name: {user_profile.user.first_name}")
        print(f"last_name: {user_profile.user.last_name}")
        print(f"work: {user_profile.work}")
        print(f"gender: {user_profile.gender}")
        print(f"custom_gender: {user_profile.custom_gender}")
        print(f"religion: {user_profile.religion}")
        print(f"date_of_birth: {date_of_birth}")
        print(f"profile_image: {user_profile.media}")
        print(f"cover_image: {user_profile.cover_image}")

        if date_of_birth:
            try:
                formatted_date = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                user_profile.date_of_birth = formatted_date
                print(f"Parsed Date: {formatted_date}")
            except ValueError:
                return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile.save()
            user_profile.user.save()
            if profile_image_data:
                user_profile.media.save()
            if cover_image_data:
                user_profile.cover_image.save()
            print("Profile Saved")
            return Response({'message': 'Profile updated successfully'})
        except Exception as e:
            print("Error:", str(e))
            return Response({'error': 'An error occurred while updating the profile.'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
