# Generated by Django 5.0.6 on 2024-07-21 19:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("feed", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="commentmedia",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="media",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="feed.commentmedia",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="comments",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="post_comments",
                to="feed.comment",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="tagged_users",
            field=models.ManyToManyField(
                blank=True, related_name="tagged_in_posts", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="post",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="feed.post"
            ),
        ),
        migrations.AddField(
            model_name="postmedia",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="media",
                to="feed.post",
            ),
        ),
        migrations.AddField(
            model_name="postmedia",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="promotedpost",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="feed.post"
            ),
        ),
        migrations.AddField(
            model_name="promotedpost",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="promotedpost",
            name="promotion_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="feed.promotionplan"
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="reaction",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="feed.reaction",
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="reaction",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="feed.reaction",
            ),
        ),
        migrations.AddField(
            model_name="reply",
            name="comment",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="feed.comment",
            ),
        ),
        migrations.AddField(
            model_name="reply",
            name="reaction",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="feed.reaction",
            ),
        ),
        migrations.AddField(
            model_name="reply",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="repost",
            name="comments",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="feed.comment",
            ),
        ),
        migrations.AddField(
            model_name="repost",
            name="post",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="feed.post"
            ),
        ),
        migrations.AddField(
            model_name="repost",
            name="reaction",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="feed.reaction",
            ),
        ),
        migrations.AddField(
            model_name="repost",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="savedpost",
            name="post",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="feed.post"
            ),
        ),
        migrations.AddField(
            model_name="savedpost",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="sharepost",
            name="shared_post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="feed.post"
            ),
        ),
        migrations.AddField(
            model_name="sharepost",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
