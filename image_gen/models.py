from django.db import models
from django.core.files.base import ContentFile
import base64
import uuid

class ImagePrompt(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    prompt = models.TextField()
    improved_prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt : {self.prompt}"

class GeneratedImageManager(models.Manager):
    """ Custom manager to encapsulate queryset logic """
    
    def create_variation(self, prompt, image_data, width, height):
        # Convert base64 image data to binary
        decoded_image = base64.b64decode(image_data)
        
        # Generate a unique filename for the image
        filename = f"{uuid.uuid4()}.png"
        
        # Wrap the binary data in a ContentFile
        content_file = ContentFile(decoded_image, name=filename)

        # Create the model instance with the image_data stored in ImageField
        return self.create(prompt=prompt, image_data=content_file, width=width, height=height)

class GeneratedImage(models.Model):
    prompt = models.ForeignKey(ImagePrompt, on_delete=models.CASCADE, related_name='images')
    image_data = models.ImageField(upload_to='generated_images/')  # Automatically uploads to S3
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Custom manager
    objects = GeneratedImageManager()

    def __str__(self):
        return f"Generated Image for {self.prompt.uuid}"

######################## TEST 2 Start ##############################

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class UnitMeasurement(models.Model):
    product = models.ForeignKey(Product, related_name='unit_measurements', on_delete=models.CASCADE)
    unit_name = models.CharField(max_length=50)  # e.g., "Pack", "Carton"
    unit_selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.unit_name}"

class ProductBatch(models.Model):
    product = models.ForeignKey(Product, related_name='batches', on_delete=models.CASCADE)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    units_sold = models.PositiveIntegerField()
    unit_type = models.CharField(max_length=50)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)

######################## TEST 2 End ##############################