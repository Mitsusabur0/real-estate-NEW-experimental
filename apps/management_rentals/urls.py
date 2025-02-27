from django.urls import path
from . import views

app_name = 'management_rentals'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('initialize-month/', views.InitializeMonthView.as_view(), name='initialize_month'),
    
    # Rental Agreements
    path('agreements/', views.RentalAgreementListView.as_view(), name='rental_agreement_list'),
    path('agreements/create/', views.RentalAgreementCreateView.as_view(), name='rental_agreement_create'),
    path('agreements/<int:pk>/', views.RentalAgreementDetailView.as_view(), name='rental_agreement_detail'),
    path('agreements/<int:pk>/update/', views.RentalAgreementUpdateView.as_view(), name='rental_agreement_update'),
    path('agreements/<int:pk>/delete/', views.RentalAgreementDeleteView.as_view(), name='rental_agreement_delete'),
    path('agreements/<int:pk>/terminate/', views.RentalAgreementTerminateView.as_view(), name='rental_agreement_terminate'),
    
    # Monthly Rentals
    path('monthly-rentals/<int:pk>/', views.MonthlyRentalDetailView.as_view(), name='monthly_rental_detail'),
    path('monthly-rentals/<int:pk>/payment/', views.RecordPaymentView.as_view(), name='record_payment'),
    path('monthly-rentals/<int:pk>/transfer/', views.RecordTransferView.as_view(), name='record_transfer'),
    
    # Reports
    path('reports/', views.ReportView.as_view(), name='report'),
]