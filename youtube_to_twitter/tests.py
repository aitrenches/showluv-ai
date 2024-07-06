from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

class YouTubeToTwitterAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('generate_thread')
        self.valid_youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        self.another_valid_youtube_url = "https://www.youtube.com/watch?v=9bZkp7q19f0"  # PSY - GANGNAM STYLE
        self.invalid_youtube_url = "https://www.youtube.com/watch?v=invalidvideoid"

    @patch('youtube_to_twitter.views.openai.Completion.create')
    def test_generate_thread_api(self, mock_openai_create):
        mock_response = MagicMock()
        mock_response.choices[0].text.strip.return_value = "Generated Twitter thread"
        mock_openai_create.return_value = mock_response

        # Test with valid URL
        response = self.client.post(self.url, {'youtube_url': self.valid_youtube_url})
        print(f"Valid URL response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 200)
        self.assertIn('twitter_thread', response.data)

        # Test with another valid URL
        response = self.client.post(self.url, {'youtube_url': self.another_valid_youtube_url})
        print(f"Another valid URL response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 200)
        self.assertIn('twitter_thread', response.data)

        # Test with invalid URL
        response = self.client.post(self.url, {'youtube_url': self.invalid_youtube_url})
        print(f"Invalid URL response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_missing_youtube_url(self):
        response = self.client.post(self.url, {})
        print(f"Missing URL response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'error': 'YouTube URL is required'})