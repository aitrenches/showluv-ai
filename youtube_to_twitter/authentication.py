from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.conf import settings

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None

        if api_key != settings.API_KEY:
            raise AuthenticationFailed('Invalid API key')

        # Use get_user_model() to get the custom user model
        User = get_user_model()
        user, _ = User.objects.get_or_create(username='api_user')
        return (user, None)