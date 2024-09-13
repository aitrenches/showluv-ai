# Image Generation App

## Overview
`image_gen` is a Django app designed to generate images using OpenAI's DALL·E 3, with the ability to resize images based on user input. The app is structured with models, serializers, views, and URL routes to create a dynamic image generation service.

## Models
The `ImagePrompt` model stores information about the prompt used to generate the image, including the improved_prompt.

The `GeneratedImage` model stores information about the image generated.

The `GeneratedImageManager` Custom manager encapsulates the queryset logic for the generated image."""

## Serializer
The `DynamicFieldsModelSerializer` is used to dynamically serialize fields from the `ImagePrompt` model. This serializer allows flexibility in including or excluding fields based on the user's needs.

**Dynamic Fields:**
- The `ImagePromptSerializer` can include fields dynamically depending on what you want to return (for example, only returning resized variations without extra metadata).

## Views
The `ImageGenerator` view is a Django class-based view that handles image generation requests. It takes a prompt, generates an image using the DALL·E 3 API, resizes it according to the specified size, and returns the resized image variations.

## URL Configuration
The app provides a single route for generating images
