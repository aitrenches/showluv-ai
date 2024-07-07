from django.urls import path
from .views import YouTubeToTwitterView

urlpatterns = [
    path('generate-thread/', YouTubeToTwitterView.as_view(), name='generate_thread'),
    # path('video-info/', VideoInfoView.as_view(), name='video_info'),
]