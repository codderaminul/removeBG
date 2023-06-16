from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('rbg/', views.home,name="rbg"),
    path('', views.ApiTemplate.as_view(), name='home'),
    path('api/', views.ImageUploadView.as_view(), name='api'),

]
