from drf_spectacular.extensions import OpenApiAuthenticationExtension
from .authentication import APIKeyAuthentication

class APIKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'youtube_to_twitter.authentication.APIKeyAuthentication'  # Use full import path as a string
    name = 'APIKey'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
        }
    
from django.conf import settings
from drf_spectacular.utils import extend_spectacular_settings

extend_spectacular_settings(settings.SPECTACULAR_SETTINGS, [
    'youtube_to_twitter.authentication_schema.APIKeyAuthenticationScheme',
])