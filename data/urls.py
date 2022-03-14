from django.urls import path
from data import views

urlpatterns = [
    path('v1', views.v1),
    path('view_all', views.view_all),
]