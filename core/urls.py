"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from . import views

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

from utility.schema_generator import CustomSchemaGenerator

swagger_info = openapi.Info(
    title="Demo APIs",
    default_version='v1',
    # description="API for summarizing YouTube videos",
    terms_of_service="TERMS OF SERVICE ON REQUEST",
    contact=openapi.Contact(email="anthonyoliko@gmail.com"),
    license=openapi.License(name="MIT License"),
)

schema_view = get_schema_view(
   openapi.Info(
    #   title="Trenches AI Staff productivity APIs",
      title="Demo APIs",
      default_version='v1',
      description="Test APIs",
      terms_of_service="TERMS OF SERVICE ON REQUEST",
      contact=openapi.Contact(email="anthonyoliko@gmail.com"),
      license=openapi.License(name="MIT LICENSE"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   generator_class=CustomSchemaGenerator,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', views.home, name='home'),
    path('api/', include('youtube_to_twitter.urls')),
    path('image_gen/', include('image_gen.urls')),
    path('test2/', include('test2.urls')),
    path('snet/', include('photrek.urls')),
]

urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)