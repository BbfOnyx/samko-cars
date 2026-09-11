from django.urls import path
from . import views, api_views

app_name = 'cars'

urlpatterns = [
    # Public views
    path('', views.car_list_view, name='list'),
    path('<int:pk>/', views.car_detail_view, name='detail'),
    path('<slug:slug>/', views.car_detail_view, name='detail_slug'),

    # REST APIs
    path('api/v1/cars/', api_views.CarListAPIView.as_view(), name='api_car_list'),
    path('api/v1/cars/<int:pk>/', api_views.CarDetailAPIView.as_view(), name='api_car_detail'),
]
