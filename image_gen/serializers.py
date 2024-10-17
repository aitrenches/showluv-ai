from rest_framework import serializers
from .models import GeneratedImage, ImagePrompt, Product, ProductBatchGood, UnitMeasurement, Category, Sale


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

######################## TEST 2 Start ##############################

class UnitMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitMeasurement
        fields = ['unit_name', 'unit_selling_price']

class ProductSerializer(serializers.ModelSerializer):
    unit_measurements = UnitMeasurementSerializer(many=True)
    category = serializers.CharField()
    
    class Meta:
        model = Product
        fields = ['name', 'quantity', 'selling_price', 'cost_price', 'category', 'unit_measurements']

    def validate_category(self, value):
        """
        Check if the category exists by name. If it doesn't exist, create it.
        """
        category_name = value.strip()  # Clean the input
        category, created = Category.objects.get_or_create(name=category_name)
        return category  # Return the Category instance (this will be saved in the Product model)

    def create(self, validated_data):
        unit_measurements_data = validated_data.pop('unit_measurements')
        category = validated_data.pop('category')  # Get the category from validated data
        product = Product.objects.create(category=category, **validated_data)
        for unit_data in unit_measurements_data:
            UnitMeasurement.objects.create(product=product, **unit_data)
        return product

class ProductBatchGoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBatchGood
        fields = ['product', 'quantity', 'cost_price', 'added_on']

class AddProductQuantitySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        # Check if the product exists
        try:
            product = Product.objects.get(id=data['product_id'])
            data['product'] = product
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        return data

    def create(self, validated_data):
        product = validated_data['product']
        quantity = validated_data['quantity']
        cost_price = validated_data['cost_price']

        # Add new batch for the product
        ProductBatchGood.objects.create(product=product, quantity=quantity, cost_price=cost_price)

        # Update product's total quantity
        product.quantity += quantity
        product.save()

        return product

class SellProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    units = serializers.IntegerField()
    unit_type = serializers.CharField()  # Pack, Carton, etc.

    def validate(self, data):
        # Check if product exists and has enough quantity
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        unit_measurement = product.unit_measurements.filter(unit_name=data['unit_type']).first()
        if not unit_measurement:
            raise serializers.ValidationError(f"Unit type {data['unit_type']} not found.")
        
        if product.quantity < data['units']:
            raise serializers.ValidationError("Insufficient quantity.")
        
        return data

    def create(self, validated_data):
        # Deduct quantity, track profit, and save sale
        product = Product.objects.get(id=validated_data['product_id'])
        product.quantity -= validated_data['units']
        product.save()
        return product

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'

######################## TEST 2 End ##############################