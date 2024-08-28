from django.urls import path
from .views import YouTubeToTwitterView, SummaryThread

urlpatterns = [
    path('generate-thread/', YouTubeToTwitterView.as_view(), name='generate_thread'),
    path('generate-summary/', SummaryThread.as_view(), name='generate_summary'),
]