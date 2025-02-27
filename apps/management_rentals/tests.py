from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from apps.management_properties.models import Property
from apps.management_clients.models import Client
from .models import RentalAgreement, MonthlyRental


class RentalAgreementModelTests(TestCase):
    """Tests for the RentalAgreement model."""
    
    def setUp(self):
        """Set up test data."""
        # Create property owner
        self.owner = Client.objects.create(
            first_name="Owner",
            last_name="Test",
            email="owner@test.com",
            phone="123456789",
            client_type="owner"
        )
        
        # Create tenant
        self.tenant = Client.objects.create(
            first_name="Tenant",
            last_name="Test",
            email="tenant@test.com",
            phone="987654321",
            client_type="tenant"
        )
        
        # Create property
        self.property = Property.objects.create(
            address="Test Address",
            current_owner=self.owner
        )
        
        # Create valid rental agreement data
        self.valid_data = {
            'property': self.property,
            'owner': self.owner,
            'tenant': self.tenant,
            'rent_amount': 500000,
            'commission_amount': 50000,
            'start_date': timezone.now().date(),
        }
    
    def test_create_rental_agreement(self):
        """Test creating a valid rental agreement."""
        agreement = RentalAgreement.objects.create(**self.valid_data)
        self.assertEqual(agreement.rent_amount, 500000)
        self.assertEqual(agreement.commission_amount, 50000)
        self.assertTrue(agreement.is_active)
    
    def test_calculate_transfer_amount(self):
        """Test calculating transfer amount."""
        agreement = RentalAgreement.objects.create(**self.valid_data)
        self.assertEqual(agreement.calculate_transfer_amount(), 450000)
    
    def test_commission_validation(self):
        """Test commission amount validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['commission_amount'] = 600000  # Greater than rent
        
        with self.assertRaises(ValidationError):
            agreement = RentalAgreement(**invalid_data)
            agreement.full_clean()
    
    def test_owner_validation(self):
        """Test owner validation."""
        invalid_data = self.valid_data.copy()
        
        # Create another client
        other_client = Client.objects.create(
            first_name="Other",
            last_name="Client",
            email="other@test.com",
            phone="555555555",
            client_type="owner"
        )
        
        invalid_data['owner'] = other_client  # Not the property owner
        
        with self.assertRaises(ValidationError):
            agreement = RentalAgreement(**invalid_data)
            agreement.full_clean()
    
    def test_termination_date_validation(self):
        """Test termination date validation."""
        agreement = RentalAgreement.objects.create(**self.valid_data)
        
        # Test valid termination date
        today = timezone.now().date()
        self.assertTrue(agreement.is_termination_date_valid(today))
        
        # Test invalid termination date (before start date)
        invalid_date = agreement.start_date - timezone.timedelta(days=1)
        self.assertFalse(agreement.is_termination_date_valid(invalid_date))
        
        # Test with end date
        agreement.end_date = today + timezone.timedelta(days=30)
        agreement.save()
        
        # Test valid termination date (within range)
        valid_date = today + timezone.timedelta(days=15)
        self.assertTrue(agreement.is_termination_date_valid(valid_date))
        
        # Test invalid termination date (after end date)
        invalid_date = today + timezone.timedelta(days=45)
        self.assertFalse(agreement.is_termination_date_valid(invalid_date))


class MonthlyRentalModelTests(TestCase):
    """Tests for the MonthlyRental model."""
    
    def setUp(self):
        """Set up test data."""
        # Create property owner
        self.owner = Client.objects.create(
            first_name="Owner",
            last_name="Test",
            email="owner@test.com",
            phone="123456789",
            client_type="owner"
        )
        
        # Create tenant
        self.tenant = Client.objects.create(
            first_name="Tenant",
            last_name="Test",
            email="tenant@test.com",
            phone="987654321",
            client_type="tenant"
        )
        
        # Create property
        self.property = Property.objects.create(
            address="Test Address",
            current_owner=self.owner
        )
        
        # Create rental agreement
        self.agreement = RentalAgreement.objects.create(
            property=self.property,
            owner=self.owner,
            tenant=self.tenant,
            rent_amount=500000,
            commission_amount=50000,
            start_date=timezone.datetime(2023, 1, 1).date(),
        )
        
        # Current date for testing
        self.today = timezone.now().date()
        
        # Current year and month
        self.current_year = self.today.year
        self.current_month = self.today.month
    
    def test_create_monthly_rental(self):
        """Test creating a valid monthly rental."""
        monthly_rental = MonthlyRental.objects.create(
            rental_agreement=self.agreement,
            period_year=self.current_year,
            period_month=self.current_month,
        )
        
        self.assertEqual(monthly_rental.rent_status, 'pending')
        self.assertEqual(monthly_rental.transfer_status, 'pending')
        self.assertEqual(monthly_rental.transfer_amount, 450000)
    
    def test_record_payment(self):
        """Test recording a payment."""
        monthly_rental = MonthlyRental.objects.create(
            rental_agreement=self.agreement,
            period_year=self.current_year,
            period_month=self.current_month,
        )
        
        # Record payment
        monthly_rental.rent_status = 'paid'
        monthly_rental.payment_date = self.today
        monthly_rental.save()
        
        self.assertEqual(monthly_rental.rent_status, 'paid')
        self.assertIsNotNone(monthly_rental.payment_date)
    
    def test_record_transfer(self):
        """Test recording a transfer."""
        monthly_rental = MonthlyRental.objects.create(
            rental_agreement=self.agreement,
            period_year=self.current_year,
            period_month=self.current_month,
            rent_status='paid',
            payment_date=self.today,
        )
        
        # Record transfer
        monthly_rental.transfer_status = 'completed'
        monthly_rental.transfer_date = self.today
        monthly_rental.save()
        
        self.assertEqual(monthly_rental.transfer_status, 'completed')
        self.assertIsNotNone(monthly_rental.transfer_date)
    
    def test_initialize_month(self):
        """Test initializing a month."""
        # Create another rental agreement
        another_agreement = RentalAgreement.objects.create(
            property=self.property,
            owner=self.owner,
            tenant=self.tenant,
            rent_amount=600000,
            commission_amount=60000,
            start_date=timezone.datetime(2023, 2, 1).date(),
        )
        
        # Initialize month
        created, existing = MonthlyRental.initialize_month(self.current_year, self.current_month)
        
        # Should create 2 new records (one for each active agreement)
        self.assertEqual(created, 2)
        self.assertEqual(existing, 0)
        
        # Check records were created
        self.assertEqual(
            MonthlyRental.objects.filter(
                period_year=self.current_year,
                period_month=self.current_month
            ).count(),
            2
        )
        
        # Initialize again - should not create new records
        created, existing = MonthlyRental.initialize_month(self.current_year, self.current_month)
        self.assertEqual(created, 0)
        self.assertEqual(existing, 2)
    
    def test_validation_requirements(self):
        """Test validation requirements."""
        monthly_rental = MonthlyRental(
            rental_agreement=self.agreement,
            period_year=self.current_year,
            period_month=self.current_month,
            rent_status='paid',  # Paid status requires payment_date
        )
        
        with self.assertRaises(ValidationError):
            monthly_rental.full_clean()
        
        monthly_rental.payment_date = self.today
        monthly_rental.transfer_status = 'completed'  # Completed status requires transfer_date
        
        with self.assertRaises(ValidationError):
            monthly_rental.full_clean()


class RentalViewsTests(TestCase):
    """Tests for rental views."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create property owner
        self.owner = Client.objects.create(
            first_name="Owner",
            last_name="Test",
            email="owner@test.com",
            phone="123456789",
            client_type="owner"
        )
        
        # Create tenant
        self.tenant = Client.objects.create(
            first_name="Tenant",
            last_name="Test",
            email="tenant@test.com",
            phone="987654321",
            client_type="tenant"
        )
        
        # Create property
        self.property = Property.objects.create(
            address="Test Address",
            current_owner=self.owner
        )
        
        # Create rental agreement
        self.agreement = RentalAgreement.objects.create(
            property=self.property,
            owner=self.owner,
            tenant=self.tenant,
            rent_amount=500000,
            commission_amount=50000,
            start_date=timezone.now().date() - timezone.timedelta(days=30),
        )
        
        # Create monthly rental
        self.monthly_rental = MonthlyRental.objects.create(
            rental_agreement=self.agreement,
            period_year=timezone.now().year,
            period_month=timezone.now().month,
        )
        
        # Login
        self.client.login(username='testuser', password='testpass123')
    
    def test_dashboard_view(self):
        """Test dashboard view."""
        url = reverse('management_rentals:dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'management_rentals/dashboard.html')
        self.assertContains(response, 'Rental Management Dashboard')
        self.assertContains(response, self.property.address)
    
    def test_rental_agreement_list_view(self):
        """Test rental agreement list view."""
        url = reverse('management_rentals:rental_agreement_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'management_rentals/rentalagreement_list.html')
        self.assertContains(response, 'Rental Agreements')
        self.assertContains(response, self.property.address)
    
    def test_rental_agreement_detail_view(self):
        """Test rental agreement detail view."""
        url = reverse('management_rentals:rental_agreement_detail', args=[self.agreement.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'management_rentals/rentalagreement_detail.html')
        self.assertContains(response, self.property.address)
        self.assertContains(response, self.owner.get_full_name())
        self.assertContains(response, self.tenant.get_full_name())
    
    def test_rental_agreement_create_view(self):
        """Test rental agreement create view."""
        url = reverse('management_rentals:rental_agreement_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'management_rentals/rentalagreement_form.html')
        self.assertContains(response, 'New Rental Agreement')
    
    def test_monthly_rental_detail_view(self):
        """Test monthly rental detail view."""
        url = reverse('management_rentals:monthly_rental_detail', args=[self.monthly_rental.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'management_rentals/monthlyrental_detail.html')
        self.assertContains(response, self.property.address)
    
    def test_record_payment_view(self):
        """Test record payment view."""
        url = reverse('management_rentals:record_payment', args=[self.monthly_rental.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'management_rentals/record_payment.html')
        self.assertContains(response, 'Record Rent Payment')
        
        # Test POST request
        post_data = {
            'rent_status': 'paid',
            'payment_date': timezone.now().date().strftime('%Y-%m-%d'),
            'notes': 'Test payment notes',
        }
        
        response = self.client.post(url, post_data)
        
        # Should redirect to monthly rental detail
        self.assertEqual(response.status_code, 302)
        
        # Check payment was recorded
        self.monthly_rental.refresh_from_db()
        self.assertEqual(self.monthly_rental.rent_status, 'paid')
        self.assertIsNotNone(self.monthly_rental.payment_date)
        self.assertEqual(self.monthly_rental.notes, 'Test payment notes')
    
    def test_initialize_month_view(self):
        """Test initialize month view."""
        url = reverse('management_rentals:initialize_month')
        
        # Delete existing monthly rental for testing
        self.monthly_rental.delete()
        
        # Test POST request
        post_data = {
            'year': timezone.now().year,
            'month': timezone.now().month,
        }
        
        response = self.client.post(url, post_data)
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Check monthly rental was created
        self.assertEqual(
            MonthlyRental.objects.filter(
                period_year=timezone.now().year,
                period_month=timezone.now().month
            ).count(),
            1
        )