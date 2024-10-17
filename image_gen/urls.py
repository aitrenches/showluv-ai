from django.urls import path
from .views import ImageGenerator, ProductCreateView, ProductDetailView, AddQuantityView, SellProductView, SalesHistoryView

urlpatterns = [
    path('generate-image/<str:size>/', ImageGenerator.as_view(), name='generate-image'),

    ######################## TEST 2 Start ##############################

    path('products/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/add-quantity/', AddQuantityView.as_view(), name='add-quantity'),
    path('products/sell/', SellProductView.as_view(), name='sell-product'),
    path('sales-history/', SalesHistoryView.as_view(), name='sales-history'),

    ######################## TEST 2 End ##############################
]
