from rest_framework import serializers

class YouTubeToTwitterInputSerializer(serializers.Serializer):
    youtube_url = serializers.URLField()

class YouTubeToTwitterOutputSerializer(serializers.Serializer):
    video_id = serializers.CharField()
    video_length = serializers.CharField()
    transcript_available = serializers.BooleanField()
    twitter_thread = serializers.ListField(child=serializers.CharField())