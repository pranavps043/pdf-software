from django.urls import path
from . import views

# Invoice URL patterns

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.invoice_list, name='home'), # Redirect root to list (which is protected)
    path('add/', views.invoice_create, name='invoice_create'),
    path('list/', views.invoice_list, name='invoice_list'),
    path('generate-pdf/<int:pk>/', views.generate_pdf, name='generate_pdf'),
    path('generate-quotation/<int:pk>/', views.generate_quotation, name='generate_quotation'),
    path('update/<int:pk>/', views.invoice_update, name='invoice_update'),
    path('delete/<int:pk>/', views.invoice_delete, name='invoice_delete'),
    
    # Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
