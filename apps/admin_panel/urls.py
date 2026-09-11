from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),

    # Dashboard home
    path('', views.dashboard_view, name='dashboard'),

    # Vehicle management
    path('cars/', views.car_list_view, name='car_list'),
    path('cars/add/', views.car_create_view, name='car_add'),
    path('cars/<int:pk>/edit/', views.car_edit_view, name='car_edit'),
    path('cars/<int:pk>/delete/', views.car_delete_view, name='car_delete'),
    path('cars/<int:pk>/status/<str:status>/', views.car_toggle_status_view, name='car_toggle_status'),
    path('cars/<int:pk>/feature/', views.car_toggle_featured_view, name='car_toggle_featured'),
    path('images/<int:img_id>/delete/', views.car_image_delete_view, name='car_image_delete'),
    path('images/<int:img_id>/set-cover/', views.car_image_set_cover_view, name='car_image_set_cover'),

    # Customer Enquiries
    path('enquiries/', views.enquiries_view, name='enquiries'),
    path('enquiries/<int:pk>/status/<str:status>/', views.enquiry_update_status_view, name='enquiry_update_status'),
    path('enquiries/<int:pk>/delete/', views.enquiry_delete_view, name='enquiry_delete'),

    # Purchase Requests
    path('purchases/', views.purchases_view, name='purchases'),
    path('purchases/<int:pk>/status/<str:status>/', views.purchase_update_status_view, name='purchase_update_status'),

    # Dealership & Homepage CMS Settings
    path('settings/', views.site_settings_view, name='settings'),
    path('social/', views.social_media_view, name='social'),
    path('social/<int:pk>/delete/', views.social_delete_view, name='social_delete'),
    path('social/<int:pk>/toggle/', views.social_toggle_view, name='social_toggle'),
    path('testimonials/', views.testimonials_view, name='testimonials'),
    path('testimonials/<int:pk>/delete/', views.testimonial_delete_view, name='testimonial_delete'),
]
