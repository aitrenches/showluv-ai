import logging
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from openai import OpenAI
from PIL import Image
from rest_framework import status, generics
from rest_framework.response import Response

from youtube_to_twitter.authentication import APIKeyAuthentication

from .models import Product, Sale, ProductBatch
from .serializers import ProductSerializer, SellProductSerializer, SaleSerializer, AddProductQuantitySerializer

# Get an instance of a logger
logger = logging.getLogger(__name__)

######################## TEST 2 Start ##############################

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        request_body=ProductSerializer,
        responses={
            status.HTTP_201_CREATED: ProductSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad Request',
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: ProductSerializer,
            status.HTTP_404_NOT_FOUND: 'Product not found',
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        lookup_value = self.kwargs.get('pk')

        try:
            # If lookup_value is an integer, assume it's a primary key
            lookup_value = int(lookup_value)
            return Product.objects.get(pk=lookup_value)
        except ValueError:
            # If ValueError occurs, it means lookup_value is not an integer, so we search by productName
            return Product.objects.get(name=lookup_value)
        except Product.DoesNotExist:
            raise Http404("Product not found.")
    
class AddProductQuantityView(generics.CreateAPIView):
    serializer_class = AddProductQuantitySerializer

    @swagger_auto_schema(
        request_body=AddProductQuantitySerializer,
        responses={
            status.HTTP_201_CREATED: "Product quantity added successfully",
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        response_data = {
            'message': f"Product {product.name} updated successfully",
            'updated_quantity': product.quantity,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class SellProductView(generics.CreateAPIView):
    serializer_class = SellProductSerializer

    @swagger_auto_schema(
        request_body=SellProductSerializer,
        responses={
            status.HTTP_200_OK: "Product sold successfully",
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity_to_sell = serializer.validated_data['quantity']

        # Track total cost and profit
        total_cost_price = 0
        batches_used = []

        # Fetch batches in FIFO order
        for batch in ProductBatch.objects.filter(product=product, remaining_quantity__gt=0).order_by('added_on'):
            if quantity_to_sell <= 0:
                break  # Exit loop when all quantities are sold

            if batch.remaining_quantity >= quantity_to_sell:
                # Fully consume this batch
                total_cost_price += quantity_to_sell * batch.cost_price
                batch.remaining_quantity -= quantity_to_sell
                batches_used.append((batch, quantity_to_sell))
                quantity_to_sell = 0
            else:
                # Partially consume this batch
                total_cost_price += batch.remaining_quantity * batch.cost_price
                quantity_to_sell -= batch.remaining_quantity
                batches_used.append((batch, batch.remaining_quantity))
                batch.remaining_quantity = 0

            batch.save()

        # Update the product's total quantity
        product.quantity -= serializer.validated_data['quantity']
        product.save()

        # Calculate selling price and profit
        total_selling_price = serializer.validated_data['quantity'] * product.selling_price
        total_profit = total_selling_price - total_cost_price

        # Save sales history (optional)
        Sale.objects.create(
            product=product,
            quantity_sold=serializer.validated_data['quantity'],
            total_selling_price=total_selling_price,
            total_cost_price=total_cost_price,
            profit=total_profit,
        )

        response_data = {
            'message': f"Product {product.name} sold successfully",
            'quantity_sold': serializer.validated_data['quantity'],
            'total_selling_price': total_selling_price,
            'total_cost_price': total_cost_price,
            'profit': total_profit,
            'batches_used': [f"Batch {batch.id}: {qty} units" for batch, qty in batches_used]
        }

        return Response(response_data, status=status.HTTP_200_OK)


class SalesHistoryView(generics.ListAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: SaleSerializer(many=True),
            status.HTTP_404_NOT_FOUND: 'Sales history not found',
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

######################## TEST 2 End ##############################