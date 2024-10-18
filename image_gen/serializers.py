from rest_framework import serializers
from .models import GeneratedImage, ImagePrompt


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields of the generated image should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Ensure fields exist in the serializer before popping them
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(
                    field_name, None
                )  # Use `pop(field_name, None)` to avoid KeyErrors when you dont specify fields in the requests


class GeneratedImageSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = GeneratedImage
        fields = ["id", "prompt", "image_data", "width", "height", "created_at"]


class ImagePromptSerializer(serializers.ModelSerializer):
    images = GeneratedImageSerializer(many=True, read_only=True)

    class Meta:
        model = ImagePrompt
        fields = ["uuid", "prompt", "improved_prompt", "created_at", "images"]

