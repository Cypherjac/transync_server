from . import views
from django.urls import path, include

urlpatterns = [
    path('identify/', views.identify, name='identify'),
    path('identify_direct/', views.identify_direct, name='identify-direct'),
]