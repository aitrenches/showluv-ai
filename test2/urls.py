from django.urls import path
from .views import ProductCreateView, ProductDetailView, AddProductQuantityView, SellProductView, SalesHistoryView

urlpatterns = [
    ######################## TEST 2 Start ##############################

    path('ovaloop/products/', ProductCreateView.as_view(), name='product-create'),
    path('ovaloop/products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('ovaloop/products/add-quantity/', AddProductQuantityView.as_view(), name='add-product-quantity'),
    path('ovaloop/products/sell/', SellProductView.as_view(), name='sell-product'),
    path('ovaloop/sales-history/', SalesHistoryView.as_view(), name='sales-history'),

    ######################## TEST 2 End ##############################
]
