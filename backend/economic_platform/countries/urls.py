from django.urls import path
from . import views

urlpatterns = [
    path('<str:country_name>/', views.country_detail, name='country_detail'),
]