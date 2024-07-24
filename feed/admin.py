from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

# Register your models here.

@admin.register(PostMedia)
class PostMedia(ImportExportModelAdmin):
    list_display = ('post','user', 'file', 'blurred_image', 'uploaded_at', 'is_sensitive')

@admin.register(CommentMedia)
class CommentMediaAdmin(ImportExportModelAdmin):
    list_display = ('media',)

@admin.register(PromotionPlan)
class PromotionPlanAdmin(ImportExportModelAdmin):
    list_display = ('name', 'description', 'price', 'duration')


@admin.register(Post)
class PostAdmin(ImportExportModelAdmin):
    list_display = ('user', 'content', 'timestamp', 'comments', 'is_business_post', 'is_personal_post')

@admin.register(SharePost)
class SharePostAdmin(ImportExportModelAdmin):
    list_display = ('user', 'caption', 'shared_post', 'timestamp')

@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin):
    list_display = ('user', 'post', 'content', 'reaction', 'timestamp')

@admin.register(Reply)
class ReplyAdmin(ImportExportModelAdmin):
    list_display = ('user', 'comment', 'content', 'reaction')


@admin.register(Reaction)
class ReactionAdmin(ImportExportModelAdmin):
    list_display = ('reaction_type',)

@admin.register(Repost)
class RepostAdmin(ImportExportModelAdmin):
    list_display = ('user', 'content', 'post', 'timestamp', 'reaction', 'comments')

@admin.register(SavedPost)
class SavedPostAdmin(ImportExportModelAdmin):
    list_display = ('user', 'post', 'timestamp')

@admin.register(PromotedPost)
class PromotedPostAdmin(ImportExportModelAdmin):
    list_display = ('user', 'post', 'promotion_plan', 'promotion_status', 'created_at')

@admin.register(AdvertCategory)
class AdvertCategoryAdmin(ImportExportModelAdmin):
    list_display = ('name',)

@admin.register(Advert)
class AdvertAdmin(ImportExportModelAdmin):
    list_display = ('title', 'category', 'duration', 'custom_duration_start', 'custom_duration_end')