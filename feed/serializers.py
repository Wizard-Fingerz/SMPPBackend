from rest_framework import serializers
from .models import *
from .models import PostMedia, CommentMedia
from user.serializers import UserSerializer, UserSerializerMain
from .utils import analyze_image, blur_image

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = '__all__'

    def create(self, validated_data):
        image = validated_data['file']
        user_sensitivity = validated_data.get('sensitivity', 'low')  # Default to 'low' if not provided

        # Debug output to ensure correct sensitivity handling
        print(f"User sensitivity setting: {user_sensitivity}")

        # Determine if the image is sensitive based on user-specified sensitivity
        user_sensitive = user_sensitivity == 'high'
        print(f"Is user sensitive? {user_sensitive}")

        # If user_sensitive or if the image is analyzed as sensitive
        is_sensitive = user_sensitive or analyze_image(image.path)
        print(f"Is the image sensitive? {is_sensitive}")
        
        validated_data['is_sensitive'] = is_sensitive
        validated_data['user_sensitive'] = user_sensitive

        # Handle image blurring if needed
        if is_sensitive:
            # Ensure the blurred_images directory exists
            blurred_images_dir = os.path.join(settings.MEDIA_ROOT, 'blurred_images')
            if not os.path.exists(blurred_images_dir):
                os.makedirs(blurred_images_dir)
            
            blurred_path = os.path.join(
                blurred_images_dir, os.path.basename(image.path)
            )
            try:
                blur_image(image.path, blurred_path)
                validated_data['blurred_image'] = os.path.join('blurred_images', os.path.basename(blurred_path))
                print(f"Blurred image saved to: {validated_data['blurred_image']}")
            except Exception as e:
                print(f"Error blurring image: {e}")

        return super().create(validated_data)


class CommentMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentMedia
        fields = '__all__'

    def create(self, validated_data):
        image = validated_data['image']
        is_sensitive = analyze_image(image.path)
        validated_data['is_sensitive'] = is_sensitive

        if is_sensitive:
            blurred_path = os.path.join(
                settings.MEDIA_ROOT, 'images', 'blurred', os.path.basename(image.path)
            )
            blur_image(image.path, blurred_path)
            validated_data['blurred_image'] = os.path.join('images', 'blurred', os.path.basename(blurred_path))

        return super().create(validated_data)

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = '__all__'

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['reaction_type']

class CommentSerializer(serializers.ModelSerializer):
    reaction = ReactionSerializer()
    
    class Meta:
        model = Comment
        fields = '__all__'

class ReplySerializer(serializers.ModelSerializer):
    reaction = ReactionSerializer()
    
    class Meta:
        model = Reply
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    file = PostMediaSerializer(many=True, required=False)
    tagged_users = UserSerializer(many=True, required=False)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = '__all__'
    
    def create(self, validated_data):
        media_data = validated_data.pop('media', [])
        tagged_users_data = validated_data.pop('tagged_users', [])
        user = self.context['request'].user
        post = Post.objects.create(user=user, **validated_data)

        for media in media_data:
            PostMedia.objects.create(post=post, **media)
        
        post.tagged_users.set(tagged_users_data)
        return post

class RepostSerializer(serializers.ModelSerializer):
    reaction = ReactionSerializer()
    comments = CommentSerializer(many=True)
    
    class Meta:
        model = Repost
        fields = '__all__'

class SavedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPost
        fields = '__all__'

class PromotedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotedPost
        fields = '__all__'


# class PostMediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PostMedia
#         fields = ('image', )


# Define document file extensions

video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.ogg', '.3gp', '.mpeg', '.vob', '.divx', '.rm', '.m4v', '.ts', '.m2ts', '.ogv', '.asf', '.mpg', '.mp2', '.m2v', '.mxf', '.mts', '.m2t', '.m1v', '.mpv']


class VideoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        # Serialize only if the associated file has a video extension
        if instance.file and any(instance.file.media.name.endswith(ext) for ext in video_extensions):
            return super().to_representation(instance)
        return None


# Define document file extensions
document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf']

class DocumentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        # Serialize only if the associated file has a document extension
        if instance.file and any(instance.file.media.name.endswith(ext) for ext in document_extensions):
            return super().to_representation(instance)
        return None

# Define audio file extensions
audio_extensions = ['.mp3', '.wav', '.ogg', '.aac', '.flac', '.wma', '.m4a', '.opus', '.amr', '.mid', '.midi', '.ac3']

class AudioPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        # Serialize only if the associated file has an audio extension
        if instance.file and any(instance.file.media.name.endswith(ext) for ext in audio_extensions):
            return super().to_representation(instance)
        return None

image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        # Serialize only if the associated file has an image extension
        if instance.file and any(instance.file.media.name.endswith(ext) for ext in image_extensions):
            return super().to_representation(instance)
        return None



others_extensions = ['.exe', '.msi', '.pkg', '.deb', '.rpm', '.dmg', '.zip', '.app', '.apk', '.jar', '.rar', '.7z', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar', '.cab', '.sit', '.sitx', '.zipx', '.z', '.lzh', '.lha', '.ace', '.arj', '.gz', '.bz2', '.xz', '.zst']

class OtherPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        # Serialize only if the associated file has an image extension
        if instance.file and any(instance.file.media.name.endswith(ext) for ext in others_extensions):
            return super().to_representation(instance)
        return None



class PostFeedSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'url', 'content', 'timestamp', 'reaction', 'comments', 'hashtag', 'is_business_post', 'is_personal_post', 'tagged_users', 'media']
