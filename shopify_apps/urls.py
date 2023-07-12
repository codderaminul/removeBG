from django.urls import path, include
from shopify_apps import views

urlpatterns = [
    path('', views.index,name="index"), 
    path('authenticate/', views.authenticate,name="authenticate"),
    path('finalize/', views.finalize,name="finalize"),
    path('logout/', views.logout,name="logout"),
    path('removeBG/<int:productId>/', views.removeBG, name="removeBG"),
]
