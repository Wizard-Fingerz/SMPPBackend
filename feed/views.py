from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.generics import *
import json
from user.utils import send_post_promotion_notification
from .models import *
from .serializers import *
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Post, PostMedia
from .serializers import PostSerializer, PostMediaSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import *
from rest_framework.decorators import *
# from paystackapi.transaction import Transaction
from django.conf import settings
from django.http import QueryDict
from django.http import FileResponse
import mimetypes

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    if request.method == 'POST':
        post_data = request.data
        print(post_data)
        post_media_data = request.FILES.getlist('media')

        tagged_users = post_data.get('tagged_users', None)
        if tagged_users:
            try:
                tagged_users = json.loads(tagged_users)
                if isinstance(post_data, QueryDict):
                    post_data = post_data.dict()
                post_data.pop('tagged_users')
            except json.JSONDecodeError as e:
                return Response({'tagged_users': [f'Invalid format: {str(e)}']}, status=status.HTTP_400_BAD_REQUEST)
        
        post_data['user'] = request.user.id

        # Add sensitivity to the post data
        sensitivity = post_data.get('sensitivity', 'low')
        post_data['sensitivity'] = sensitivity

        post_serializer = PostSerializer(data=post_data, context={'request': request})
        if post_serializer.is_valid():
            post = post_serializer.save()

            if post_media_data:
                for media in post_media_data:
                    media_data = {
                        'post': post.id,
                        'user': request.user.id,
                        'file': media,
                        'sensitivity': sensitivity  # Pass the sensitivity level
                    }

                    media_serializer = PostMediaSerializer(data=media_data)
                    if media_serializer.is_valid():
                        media_serializer.save()
                    else:
                        print("Media Serializer Errors:", media_serializer.errors)

            if tagged_users:
                post.tagged_users.set(tagged_users)

            return Response(post_serializer.data, status=status.HTTP_201_CREATED)

        print("Post Serializer Errors:", post_serializer.errors)
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def post_feed(request):
    # Retrieve the UserProfile associated with the current user
    user_profile = request.user.userprofile

    # Retrieve the stickers of the current user's profile
    sticking_users = user_profile.stickers.all()

    # Retrieve posts from users that the current user follows, ordered by timestamp
    posts = Post.objects.filter(user__userprofile__in=sticking_users).order_by('-timestamp')

    # Serialize the posts
    post_serializer = PostSerializer(
        posts, many=True, context={'request': request})

    return Response(post_serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_post(request, post_id):
    try:
        # Retrieve the post by its ID
        post = Post.objects.get(pk=post_id)

        # Serialize the post
        post_serializer = PostSerializer(post, context={'request': request})

        return Response(post_serializer.data, status=status.HTTP_200_OK)

    except Post.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_post(request, post_id):
    try:
        # Retrieve the post by its ID
        post = Post.objects.get(pk=post_id)

        # Check if the current user is the author of the post
        if post.user != request.user:
            return Response({'detail': 'You do not have permission to update this post.'}, status=status.HTTP_403_FORBIDDEN)

        # Deserialize the request data and update the post
        post_serializer = PostSerializer(post, data=request.data, partial=True)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Post.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    try:
        # Retrieve the post by its ID
        post = Post.objects.get(pk=post_id)

        # Check if the current user is the author of the post
        if post.user != request.user:
            return Response({'detail': 'You do not have permission to delete this post.'}, status=status.HTTP_403_FORBIDDEN)

        # Delete the post
        post.delete()

        return Response({'detail': 'Post deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    except Post.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_post(request, post_id):
    try:
        # Retrieve the post by its ID
        post = Post.objects.get(pk=post_id)

        # Check if the request user is the author of the post
        if post.user != request.user:
            return Response({'detail': 'You do not have permission to edit this post.'}, status=status.HTTP_403_FORBIDDEN)

        # Update the post data with the request data
        post_serializer = PostSerializer(post, data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Post.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


# Admin posts

@api_view(['POST'])
@permission_classes([IsAdminUser])  # Only admin can create posts
def admin_create_post(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View to view all posts
@api_view(['GET'])
def admin_view_posts(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# View to edit a post
@api_view(['PUT'])

@permission_classes([IsAdminUser])  # Only admin can edit posts
def admin_edit_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Post.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

# View to delete a post
@api_view(['DELETE'])
@permission_classes([IsAdminUser])  # Only admin can delete posts
def admin_delete_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        post.delete()
        return Response({'detail': 'Post deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except Post.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


# End of Admin posts


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    try:
        # Retrieve the post by its ID
        post = Post.objects.get(pk=post_id)

        # Create a new comment associated with the post and the current user
        comment_data = {
            'text': request.data.get('text'),  # Replace 'text' with the field name for your comment content
            'post': post,
            'user': request.user,
        }

        comment_serializer = CommentSerializer(data=comment_data)
        if comment_serializer.is_valid():
            comment_serializer.save()
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Post.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_comments(request, post_id):
    try:
        # Retrieve the post by its ID
        post = Post.objects.get(pk=post_id)

        # Retrieve comments associated with the post
        comments = Comment.objects.filter(post=post)

        # Serialize the comments
        comment_serializer = CommentSerializer(comments, many=True)

        return Response(comment_serializer.data, status=status.HTTP_200_OK)

    except Post.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


class PostMediaViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = PostMedia.objects.all()
    serializer_class = PostMediaSerializer


class ReactionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_replies(request, post_id, comment_id):
    try:
        # Retrieve the comment by its ID within the specified post
        comment = Comment.objects.get(pk=comment_id, post__pk=post_id)

        # Retrieve replies associated with the comment
        replies = Reply.objects.filter(comment=comment)

        # Serialize the replies
        reply_serializer = ReplySerializer(replies, many=True)

        return Response(reply_serializer.data, status=status.HTTP_200_OK)

    except Comment.DoesNotExist:
        return Response({'detail': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reply(request, post_id, comment_id):
    try:
        # Retrieve the comment by its ID within the specified post
        comment = Comment.objects.get(pk=comment_id, post__pk=post_id)

        # Create a new reply associated with the comment and the current user
        reply_data = {
            'text': request.data.get('text'),  # Replace 'text' with the field name for your reply content
            'comment': comment,
            'user': request.user,
        }

        reply_serializer = ReplySerializer(data=reply_data)
        if reply_serializer.is_valid():
            reply_serializer.save()
            return Response(reply_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(reply_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Comment.DoesNotExist:
        return Response({'detail': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)

class ReplyViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Post.objects.all().order_by('timestamp')
    serializer_class = PostSerializer
    
    def get_queryset(self):
        return Post.objects.all().select_related('user').prefetch_related('postmedia_set').order_by('-timestamp')

    @action(detail=True, methods=['POST'])
    def share_post(self, request, pk=None):
        post = self.get_object()
        
        # Create a new Share instance to record the sharing
        SharePost.objects.create(user=request.user, shared_post=post)
        
        return Response({"detail": "Post shared successfully."}, status=status.HTTP_201_CREATED)

class PostFeedsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Post.objects.all().order_by('-timestamp')
    serializer_class = PostFeedSerializer

    # def get_queryset(self):
    #     return Post.objects.all().select_related('user').prefetch_related('media').order_by('-timestamp')

class DownloadMediaView(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, media_id):
        try:
            media = PostMedia.objects.get(pk=media_id)
        except PostMedia.DoesNotExist:
            return Response({"detail": "Media not found."}, status=status.HTTP_404_NOT_FOUND)

        file_path = media.blurred_image.path if media.is_sensitive else media.file.path

        if not os.path.exists(file_path):
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        # Guess the MIME type based on the file extension
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'  # Fallback if mime type can't be determined

        response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'

        return response

class RepostViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Repost.objects.all()
    serializer_class = RepostSerializer


class SavedPostViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = SavedPost.objects.all()
    serializer_class = SavedPostSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_reaction(request, content_type, object_id, reaction_type):
    try:
        # Determine the content type (Comment, Reply, or Post)
        if content_type == 'comment':
            content_object = Comment.objects.get(pk=object_id)
        elif content_type == 'reply':
            content_object = Reply.objects.get(pk=object_id)
        elif content_type == 'post':
            content_object = Post.objects.get(pk=object_id)
        else:
            return Response({'detail': 'Invalid content type.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a reaction of the same type already exists for the user and content object
        existing_reaction = Reaction.objects.filter(
            user=request.user, content_type=content_type, object_id=object_id, reaction_type=reaction_type
        ).first()

        if existing_reaction:
            # If a reaction of the same type exists, remove it (toggle)
            existing_reaction.delete()
            return Response({'detail': 'Reaction removed successfully.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            # Create a new reaction
            reaction_data = {
                'user': request.user,
                'content_type': content_type,
                'object_id': object_id,
                'reaction_type': reaction_type,
            }

            reaction_serializer = ReactionSerializer(data=reaction_data)
            if reaction_serializer.is_valid():
                reaction_serializer.save()
                return Response(reaction_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(reaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Comment.DoesNotExist:
        return Response({'detail': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Reply.DoesNotExist:
        return Response({'detail': 'Reply not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Post.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reactions(request, content_type, object_id):
    try:
        # Determine the content type (Comment, Reply, or Post)
        content_type = content_type.lower()
        if content_type not in ['comment', 'reply', 'post']:
            return Response({'detail': 'Invalid content type.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve reactions for the specified content object
        if content_type == 'post':
            content_object = Post.objects.get(pk=object_id)
        elif content_type == 'comment':
            content_object = Comment.objects.get(pk=object_id)
        elif content_type == 'reply':
            content_object = Reply.objects.get(pk=object_id)

        # Retrieve reactions associated with the content object
        reactions = Reaction.objects.filter(content_object=content_object)

        # Count the number of users who reacted
        reacting_users_count = reactions.values('user').distinct().count()

        # Serialize the reactions
        reaction_serializer = ReactionSerializer(reactions, many=True)

        # Get the list of users reacting to the content
        reacting_users = reactions.values('user').distinct()
        user_ids = [user['user'] for user in reacting_users]

        # Serialize the user IDs and their reactions
        user_reactions = []
        for user_id in user_ids:
            user = User.objects.get(pk=user_id)
            user_reactions.append({
                'user_id': user_id,
                'username': user.username,
                'reactions': [r['reaction_type'] for r in reactions.filter(user=user)],
            })

        return Response({
            'reacting_users_count': reacting_users_count,
            'reactions': reaction_serializer.data,
            'reacting_users': user_reactions,  # Include the list of users reacting
        }, status=status.HTTP_200_OK)

    except (Post.DoesNotExist, Comment.DoesNotExist, Reply.DoesNotExist):
        return Response({'detail': 'Content object not found.'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_reaction(request, object_type, object_id):
    try:
        user = request.user
        reaction_data = request.data
        reaction_data['user'] = user.id  # Add user ID to the reaction data

        # Determine the object type (post, comment, or reply) and object instance
        if object_type == 'post':
            obj = Post.objects.get(pk=object_id)
        elif object_type == 'comment':
            obj = Comment.objects.get(pk=object_id)
        elif object_type == 'reply':
            obj = Reply.objects.get(pk=object_id)
        else:
            return Response({'detail': 'Invalid object type.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a reaction already exists for this user and object
        existing_reaction = Reaction.objects.filter(user=user, object_id=object_id).first()

        if existing_reaction:
            # If a reaction exists, update it with the new reaction type
            serializer = ReactionSerializer(existing_reaction, data=reaction_data)
        else:
            # If no reaction exists, create a new one
            serializer = ReactionSerializer(data=reaction_data)

        if serializer.is_valid():
            serializer.save(object=obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Post.DoesNotExist:
        return Response({'detail': 'Object not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_reaction(request, object_type, object_id):
    try:
        user = request.user
        reaction_data = request.data
        reaction_data['user'] = user.id

        # Determine the object type (post, comment, or reply) and object instance
        if object_type == 'post':
            obj = Post.objects.get(pk=object_id)
        elif object_type == 'comment':
            obj = Comment.objects.get(pk=object_id)
        elif object_type == 'reply':
            obj = Reply.objects.get(pk=object_id)
        else:
            return Response({'detail': 'Invalid object type.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a reaction already exists for this user and object
        existing_reaction = Reaction.objects.filter(user=user, object_id=object_id).first()

        if existing_reaction:
            # If a reaction exists, delete it
            existing_reaction.delete()
            return Response({'detail': 'Reaction removed.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            # If no reaction exists, create a new one
            serializer = ReactionSerializer(data=reaction_data)

            if serializer.is_valid():
                serializer.save(object=obj)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Post.DoesNotExist:
        return Response({'detail': 'Object not found.'}, status=status.HTTP_404_NOT_FOUND)



# Search Post
class PostSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')

        if query:
            # Perform a case-insensitive search across relevant fields in the database
            results = Post.objects.filter(
                Q(user__icontains=query) |
                Q(content__icontains=query) |
                Q(hashtag__icontains=query)
            )
            serializer = PostSerializer(results, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)


class VideoPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VideoPostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        # Filter posts to include only those with video file extensions
        return Post.objects.filter(file__media__name__endswith=tuple(video_extensions))


class DocumentPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentPostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        # Filter posts to include only those with document file extensions
        return Post.objects.filter(file__media__name__endswith=tuple(document_extensions))


class AudioPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AudioPostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        # Filter posts to include only those with audio file extensions
        return Post.objects.filter(file__media__name__endswith=tuple(audio_extensions))



class ImagePostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ImagePostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        # Filter posts to include only those with image file extensions
        return Post.objects.filter(file__media__name__endswith=tuple(image_extensions))


class OtherPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OtherPostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        return Post.objects.filter(file__media__name__endswith=tuple(others_extensions))



class PromotePostViewSet(viewsets.ModelViewSet):
    serializer_class = PromotedPostSerializer
    queryset = PromotedPost.objects.all()

    def create(self, request, *args, **kwargs):
        # Get the selected promotion plan ID and post ID from the request
        plan_id = request.data.get('plan_id')
        post_id = request.data.get('post_id')  # Assuming you expect 'post_id' in the request

        try:
            # Retrieve the selected promotion plan
            promotion_plan = PromotionPlan.objects.get(pk=plan_id)

            # Calculate the payment amount based on the selected plan
            payment_amount = promotion_plan.price

            # Initialize a Paystack transaction with the calculated amount
            transaction_params = {
                "reference": f"post_promotion_{post_id}",
                "amount": payment_amount * 100,  # Amount in kobo
                "email": request.user.email,  # User's email
                "metadata": {"post_id": post_id, "promotion_plan_id": plan_id},
            }
            transaction_response = Transaction.initialize(**transaction_params)

            # Return the Paystack authorization URL to the frontend
            return Response({'authorization_url': transaction_response['data']['authorization_url']})

        except PromotionPlan.DoesNotExist:
            return Response({'detail': 'Promotion plan not found.'}, status=status.HTTP_404_NOT_FOUND)


class PaystackCallbackView(APIView):
    def get(self, request):
        reference = request.GET.get('reference')

        # Verify the payment status with Paystack
        verify_response = Transaction.verify(reference)

        if verify_response['data']['status'] == 'success':
            # Payment was successful, create the promoted post record

            # Extract the post_id from the metadata
            post_id = verify_response['data']['metadata']['post_id']

            # Create the promoted post record here and update promotion_status

            # Send a notification to the user
            user = request.user  # Assuming you have the user available in the request
            message = 'Your post has been successfully promoted!'
            send_post_promotion_notification(user, message)

            return Response({'detail': 'Payment successful.'})
        else:
            return Response({'detail': 'Payment failed.'})


class UserPostsView(ListAPIView):
    serializer_class = PostSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter posts by the authenticated user
        user = self.request.user
        return Post.objects.filter(user=user)
    
    
    
# Image privacy settings

class PostMediaViewSet(viewsets.ModelViewSet):
    queryset = PostMedia.objects.all()
    serializer_class = PostMediaSerializer
    permission_classes = [IsAuthenticated]

class CommentMediaViewSet(viewsets.ModelViewSet):
    queryset = CommentMedia.objects.all()
    serializer_class = CommentMediaSerializer
    permission_classes = [IsAuthenticated]