from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('home', views.home,name="home"),
    path('rbg/', views.ApiTemplate.as_view(), name='rbg'),
    path('api/', views.ImageUploadView.as_view(), name='api'),
    path('setBG/', views.setBG.as_view(), name='setBG'),
]


# https://cdn.shopify.com/s/files/1/0769/6452/8446/files/home-image_f91cb327-f4ae-4b4b-a203-6f518aa0b3b1.jpg?v=1689011683
# https://cdn.shopify.com/s/files/1/0769/6452/8446/files/home-image_f91cb327-f4ae-4b4b-a203-6f518aa0b3b1.jpg?v=1689011683