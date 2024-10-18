from django.db import models

# Create your models here.

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
    product = models.ForeignKey(Product, related_name='product_batch', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=True)
    remaining_quantity = models.PositiveIntegerField(null=True)  # Tracks unsold quantity
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="example: 500.50", null=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Batch for {self.product.name} - {self.quantity} units at {self.cost_price} each"

    def save(self, *args, **kwargs):
        # Automatically set remaining quantity on create
        if not self.pk:
            self.remaining_quantity = self.quantity
        super().save(*args, **kwargs)

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField(default=0)
    total_selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.quantity_sold} units of {self.product.name}"


######################## TEST 2 End ##############################