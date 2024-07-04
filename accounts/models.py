from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    
    # Add any additional fields you might need
    # For example:
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.username