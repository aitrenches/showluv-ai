from rest_framework import serializers
from .models import Product, ProductBatch, UnitMeasurement, Category, Sale

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

class ProductBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBatch
        fields = ['product', 'quantity', 'cost_price', 'added_on']


class AddProductQuantitySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        # Check if the product exists
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        return data

    def create(self, validated_data):
        product_id = validated_data['product_id']
        quantity = validated_data['quantity']
        cost_price = validated_data['cost_price']

        # Fetch product
        product = Product.objects.get(pk=product_id)

        # Add new batch for the product
        ProductBatch.objects.create(product=product, quantity=quantity, cost_price=cost_price)

        # Update product's total quantity
        product.quantity += quantity
        product.save()

        return product  # Return the updated product instance


class SellProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    unit_measurement = serializers.CharField()  # Optional: If selling in different units

    def validate(self, data):
        try:
            product = Product.objects.get(id=data['product_id'])
            data['product'] = product
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        
        if data['quantity'] > product.quantity:
            raise serializers.ValidationError(f"Not enough stock available. Only {product.quantity} units in stock.")
        
        return data


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'

######################## TEST 2 End ##############################