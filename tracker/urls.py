from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('add/', views.add_expense, name='add_expense'),  # Add expense page
    path('result/', views.result, name='result'),  # Result page
]
