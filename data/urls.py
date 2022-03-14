from django.urls import path
from data import views

urlpatterns = [
    path('v3', views.v3)
]