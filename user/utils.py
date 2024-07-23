from user.models import Notification
from .models import UserProfile


def send_notification(recipient, sender, message):
    notification = Notification(recipient=recipient, sender=sender, message=message)
    notification.save()


# Assuming you have a User model and a UserProfile model that stores user behavior

def get_frequently_searched_polls(user):
    # Retrieve the user's frequently searched polls
    # Example: Assuming UserProfile has a 'searched_polls' field
    frequently_searched_polls = user.userprofile.searched_polls.all()
    return frequently_searched_polls


def send_post_promotion_notification(user, message):
    # Create a notification for the user
    Notification.objects.create(
        recipient=user,
        verb='promoted_post',  # You can customize this verb based on your app's notification system
        description=message,
    )