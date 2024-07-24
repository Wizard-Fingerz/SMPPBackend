import logging
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.contentmoderator import ContentModeratorClient
from msrest.authentication import CognitiveServicesCredentials
from django.conf import settings
from PIL import Image as PilImage, ImageFilter
import os

# Set up logging
logger = logging.getLogger(__name__)

# Print out the settings for debugging purposes
print(f'{settings.AZURE_CV_ENDPOINT}')
print(f'{settings.AZURE_CV_SUBSCRIPTION_KEY}')
print(f'{settings.AZURE_CM_ENDPOINT}')
print(f'{settings.AZURE_CM_SUBSCRIPTION_KEY}')

print(f"Computer Vision subscription key: {settings.AZURE_CV_SUBSCRIPTION_KEY}")
print(f"Computer Vision endpoint: {settings.AZURE_CV_ENDPOINT}")

def analyze_image(image_path):
    if not os.path.exists(image_path):
        logger.error(f"Image path does not exist: {image_path}")
        return False  # Or handle accordingly based on your application logic

    try:
        # Fetching subscription keys and endpoints from settings
        cv_subscription_key = settings.AZURE_CV_SUBSCRIPTION_KEY
        cv_endpoint = settings.AZURE_CV_ENDPOINT
        cm_subscription_key = settings.AZURE_CM_SUBSCRIPTION_KEY
        cm_endpoint = settings.AZURE_CM_ENDPOINT

        # Logging for debugging purposes
        logger.info(f"Computer Vision subscription key: {cv_subscription_key}")
        logger.info(f"Computer Vision endpoint: {cv_endpoint}")
        logger.info(f"Content Moderator subscription key: {cm_subscription_key}")
        logger.info(f"Content Moderator endpoint: {cm_endpoint}")

        if not cv_subscription_key or not cm_subscription_key:
            raise ValueError("Subscription key cannot be None")

        # Azure Computer Vision Client
        cv_client = ComputerVisionClient(
            cv_endpoint,
            CognitiveServicesCredentials(cv_subscription_key)
        )

        with open(image_path, 'rb') as image_file:
            cv_analysis = cv_client.analyze_image_in_stream(
                image_file, visual_features=[VisualFeatureTypes.adult]
            )

        is_sensitive = cv_analysis.adult.is_adult_content or cv_analysis.adult.is_racy_content

        logger.info(f"Azure CV analysis for {image_path}: Adult content: {cv_analysis.adult.is_adult_content}, Racy content: {cv_analysis.adult.is_racy_content}")
        print(f"Azure CV analysis for {image_path}: Adult content: {cv_analysis.adult.is_adult_content}, Racy content: {cv_analysis.adult.is_racy_content}")

        # Azure Content Moderator Client
        cm_client = ContentModeratorClient(
            cm_endpoint,
            CognitiveServicesCredentials(cm_subscription_key)
        )

        with open(image_path, 'rb') as image_file:
            cm_analysis = cm_client.image_moderation.evaluate_file_input(
                image_file, data_representation="URL", cache_content=False
            )

        is_sensitive = is_sensitive or cm_analysis.is_image_adult_classified or cm_analysis.is_image_racy_classified

        logger.info(f"Azure Content Moderator analysis for {image_path}: Adult classified: {cm_analysis.is_image_adult_classified}, Racy classified: {cm_analysis.is_image_racy_classified}")
        print(f"Azure Content Moderator analysis for {image_path}: Adult classified: {cm_analysis.is_image_adult_classified}, Racy classified: {cm_analysis.is_image_racy_classified}")

        return is_sensitive
    except Exception as e:
        logger.error(f"Error analyzing image {image_path}: {str(e)}")
        return False

def blur_image(image_path, output_path):
    try:
        image = PilImage.open(image_path)
        blurred_image = image.filter(ImageFilter.GaussianBlur(50))  # Increase the blur radius for heavy blurring
        blurred_image.save(output_path)
        logger.info(f"Image successfully blurred and saved to {output_path}")
    except Exception as e:
        logger.error(f"Error blurring image {image_path}: {str(e)}")
