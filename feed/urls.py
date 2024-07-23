# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'postmedia', PostMediaViewSet)
router.register(r'reaction', ReactionViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'reply', ReplyViewSet)
router.register(r'post', PostViewSet)
router.register(r'repost', RepostViewSet)
router.register(r'savedpost', SavedPostViewSet)
router.register(r'video-posts', VideoPostViewSet, basename = "video-posts")
router.register(r'document-posts', DocumentPostViewSet, basename = "document-post")
router.register(r'audio-posts', AudioPostViewSet, basename = "audio-post")
router.register(r'image-posts', ImagePostViewSet, basename = "image-post")
router.register(r'other-posts', OtherPostViewSet, basename = "other-post")
router.register(r'promote-posts', PromotePostViewSet, basename = "promote-post")
router.register(r'post-media', PostMediaViewSet, basename='post-media')
router.register(r'comment-media', CommentMediaViewSet, basename='comment-media')

router.register(r'post-feeds', PostFeedsViewSet, basename='post-feeds')



urlpatterns = [
    path('', include(router.urls)),
    path('sticking-post-feed/', post_feed, name='post_feed'),
    path('create-post/', create_post, name='post_feed'),
    path('post/<int:post_id>/', retrieve_post, name='retrieve-post'),
    path('post/<int:post_id>/', update_post, name='update-post'),
    path('post/<int:post_id>/', delete_post, name='delete-post'),
    path('post/<int:post_id>/comments/', view_comments, name='view-comments'),
    path('post/<int:post_id>/comment/', create_comment, name='create-comment'),
    path('comment/<int:comment_id>/replies/', view_replies, name='view-replies'),
    path('view-reply/<int:post_id>/comment/<int:comment_id>/replies/', view_replies, name='view-replies'),
    path('create-reply/<int:post_id>/comment/<int:comment_id>/replies/', create_reply, name='create-reply'),
    path('add-reaction/<str:content_type>/<int:object_id>/<str:reaction_type>/', add_reaction, name='add-reaction'),
    path('get-reactions/<str:content_type>/<int:object_id>/', get_reactions, name='get-reactions'),
    path('edit-post/<int:post_id>/', edit_post, name='edit-post'),
    path('create-or-update-reaction/<str:object_type>/<int:object_id>/', create_or_update_reaction, name='create-or-update-reaction'),
    path('toggle-reaction/<str:object_type>/<int:object_id>/', toggle_reaction, name='toggle-reaction'),

    path('post-search/', PostSearchAPIView.as_view(), name='post-search'),
    
    path('paystack-callback/', PaystackCallbackView.as_view(), name='paystack-callback'),
    
    path('download-media/<int:media_id>/', DownloadMediaView.as_view(), name='download_media'),


    # Admin user endpoints
    path('admin-create-post/', admin_create_post, name='create-post'),
    path('admin-view-posts/', admin_view_posts, name='view-posts'),
    path('admin-edit-post/<int:post_id>/', admin_edit_post, name='edit-post'),
    path('admin-delete-post/<int:post_id>/', admin_delete_post, name='delete-post'),

]
