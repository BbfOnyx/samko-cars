from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('request/', views.submit_purchase_request, name='request'),
]
