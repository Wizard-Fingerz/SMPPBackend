

# utils.py
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from django.conf import settings
from PIL import Image as PilImage, ImageFilter
import os


def analyze_image(image_path):
    if not os.path.exists(image_path):
        return False  # Or handle accordingly based on your application logic

    client = ComputerVisionClient(
        settings.AZURE_ENDPOINT, 
        CognitiveServicesCredentials(settings.AZURE_SUBSCRIPTION_KEY)
    )

    with open(image_path, 'rb') as image_file:
        analysis = client.analyze_image_in_stream(
            image_file, visual_features=[VisualFeatureTypes.adult]
        )

    is_sensitive = analysis.adult.is_adult_content or analysis.adult.is_racy_content
    return is_sensitive


def blur_image(image_path, output_path):
    image = PilImage.open(image_path)
    blurred_image = image.filter(ImageFilter.GaussianBlur(10))  # Adjust the blur radius as needed
    blurred_image.save(output_path)
