from django.contrib import admin
from .models import GeneratedImage, ImagePrompt

@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('prompt', 'image_data', 'width', 'height', 'created_at')
    # search_fields = ('prompt__text',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

@admin.register(ImagePrompt)
class ImagePromptAdmin(admin.ModelAdmin):
    list_display = ('prompt', 'created_at')
    search_fields = ('prompt',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
