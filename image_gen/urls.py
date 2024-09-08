from django.urls import path
from .views import ImageGenerator

urlpatterns = [
    path('generate-image/<str:size>/', ImageGenerator.as_view(), name='generate-image'),
]