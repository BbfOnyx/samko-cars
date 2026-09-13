from io import BytesIO
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from django.conf import settings
from PIL import Image
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch
from apps.cars.models import Car, Feature, CarImage
from apps.core.models import SiteSetting, SocialMedia, Testimonial
from apps.enquiries.models import Enquiry
from apps.purchases.models import PurchaseRequest

class SamkoCarsFullTestSuite(TestCase):
    def setUp(self):
        # Setup settings
        self.settings = SiteSetting.get_settings()
        self.settings.whatsapp_number = "2348012345678"
        self.settings.site_name = "Samko Cars"
        self.settings.save()

        # Admin superuser
        self.admin = User.objects.create_superuser('admin_test', 'admin@test.com', 'Pass12345!')
        
        # Regular non-staff user
        self.user = User.objects.create_user('normal_user', 'user@test.com', 'Pass12345!')

        # Car features
        self.f_ac = Feature.objects.create(name="Air Conditioning", icon_name="❄️")
        self.f_cam = Feature.objects.create(name="Reverse Camera", icon_name="📷")

        # Test Cars
        self.car1 = Car.objects.create(
            make="Toyota",
            model="Camry XSE",
            year=2021,
            price=Decimal("25000000"),
            mileage=32000,
            condition="foreign_used",
            transmission="automatic",
            fuel_type="petrol",
            body_type="sedan",
            location="Lekki, Lagos",
            status="available",
            is_featured=True,
            is_active=True
        )
        self.car1.features.add(self.f_ac, self.f_cam)

        self.car2 = Car.objects.create(
            make="Mercedes-Benz",
            model="GLE 450",
            year=2022,
            price=Decimal("78000000"),
            mileage=19000,
            condition="foreign_used",
            transmission="automatic",
            fuel_type="petrol",
            body_type="suv",
            location="Victoria Island, Lagos",
            status="reserved",
            is_featured=False,
            is_active=True
        )

        self.client = Client()

    def _uploaded_image(self, name, image_format='JPEG'):
        buffer = BytesIO()
        Image.new('RGB', (20, 20), color='navy').save(buffer, format=image_format)
        return SimpleUploadedFile(
            name,
            buffer.getvalue(),
            content_type=f'image/{image_format.lower()}',
        )

    # 1. Public Pages
    def test_homepage_loads(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Samko Cars")
        self.assertContains(response, "Camry XSE")

    def test_about_page_loads(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About Samko Cars")

    def test_contact_page_loads(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contact Us")
        self.assertContains(response, "2348012345678")

    # 2. Inventory & Filtering
    def test_cars_inventory_page_and_filtering(self):
        # All cars
        response = self.client.get(reverse('cars:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Camry XSE")
        self.assertContains(response, "GLE 450")

        # Filter by make=Toyota
        resp_toyota = self.client.get(reverse('cars:list') + '?make=Toyota')
        self.assertEqual(resp_toyota.status_code, 200)
        self.assertContains(resp_toyota, "Camry XSE")
        self.assertNotContains(resp_toyota, "GLE 450")

        # Filter by body_type=suv
        resp_suv = self.client.get(reverse('cars:list') + '?body_type=suv')
        self.assertEqual(resp_suv.status_code, 200)
        self.assertContains(resp_suv, "GLE 450")
        self.assertNotContains(resp_suv, "Camry XSE")

        # Filter by price range
        resp_price = self.client.get(reverse('cars:list') + '?min_price=50000000')
        self.assertEqual(resp_price.status_code, 200)
        self.assertContains(resp_price, "GLE 450")
        self.assertNotContains(resp_price, "Camry XSE")

    def test_car_detail_page(self):
        response = self.client.get(reverse('cars:detail', args=[self.car1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2021 Toyota Camry XSE")
        self.assertContains(response, "25,000,000")
        self.assertContains(response, "Air Conditioning")

    # 3. Enquiries (AJAX & Non-AJAX)
    def test_enquiry_submission_ajax(self):
        response = self.client.post(
            reverse('enquiries:submit'),
            {
                'car_id': self.car1.id,
                'name': 'Emeka Obi',
                'email': 'emeka@example.com',
                'phone': '+2348011112222',
                'message': 'Is this vehicle still available for inspection tomorrow?',
                'is_ajax': '1',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data.get('success'))
        self.assertEqual(Enquiry.objects.filter(email='emeka@example.com').count(), 1)

    def test_enquiry_submission_standard_post(self):
        response = self.client.post(
            reverse('enquiries:submit'),
            {
                'car_id': self.car1.id,
                'name': 'Tunde Bakare',
                'email': 'tunde@example.com',
                'phone': '+2348022223333',
                'message': 'Looking for test drive appointment.',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Enquiry.objects.filter(email='tunde@example.com').count(), 1)

    # 4. Purchases / Reservations (AJAX & Non-AJAX)
    def test_purchase_request_submission_ajax(self):
        response = self.client.post(
            reverse('purchases:request'),
            {
                'car_id': self.car1.id,
                'customer_name': 'Amina Bello',
                'customer_email': 'amina@example.com',
                'customer_phone': '+2348033334444',
                'inspection_date': '2026-10-15',
                'message': 'I want to initiate purchase and arrange test drive.',
                'is_ajax': '1',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data.get('success'))
        self.assertEqual(PurchaseRequest.objects.filter(customer_email='amina@example.com').count(), 1)
        req = PurchaseRequest.objects.get(customer_email='amina@example.com')
        self.assertEqual(req.price_at_request, Decimal("25000000"))

    def test_purchase_request_submission_standard_post(self):
        response = self.client.post(
            reverse('purchases:request'),
            {
                'car_id': self.car1.id,
                'customer_name': 'Ngozi Eze',
                'customer_email': 'ngozi@example.com',
                'customer_phone': '+2348099998888',
                'inspection_date': '2026-10-20',
                'message': 'Please reserve this vehicle for inspection.',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PurchaseRequest.objects.filter(customer_email='ngozi@example.com').count(), 1)

    # 5. Security & Authentication
    def test_admin_dashboard_security(self):
        # Unauthenticated user redirected to login
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin-panel/login', response.url)

        # Non-staff user denied
        self.client.force_login(self.user)
        response_non_staff = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response_non_staff.status_code, 302)

        # Authenticated staff user granted access
        self.client.force_login(self.admin)
        response_auth = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response_auth.status_code, 200)
        self.assertContains(response_auth, "Dashboard")

    # 6. Admin Car CRUD
    def test_admin_create_car(self):
        self.client.force_login(self.admin)
        create_url = reverse('admin_panel:car_add')
        post_data = {
            'make': 'Lexus',
            'model': 'RX 350',
            'year': '2020',
            'price': '38000000',
            'mileage': '45000',
            'condition': 'foreign_used',
            'transmission': 'automatic',
            'fuel_type': 'petrol',
            'body_type': 'suv',
            'engine': '3.5L V6',
            'exterior_color': 'Pearl White',
            'interior_color': 'Tan Leather',
            'location': 'Ikeja, Lagos',
            'status': 'available',
            'is_featured': 'on',
            'is_active': 'on',
            'description': 'Pristine condition Lexus RX 350.',
            'features': [self.f_ac.id]
        }
        response = self.client.post(create_url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Car.objects.filter(make='Lexus', model='RX 350').exists())

    def test_admin_create_car_persists_multiple_uploaded_images(self):
        self.client.force_login(self.admin)
        create_url = reverse('admin_panel:car_add')
        first = self._uploaded_image(f"new-front-{uuid4().hex}.jpg")
        second = self._uploaded_image(f"new-side-{uuid4().hex}.jpg")
        post_data = {
            'make': 'Honda', 'model': 'Accord Sport', 'year': '2022',
            'price': '30000000', 'mileage': '21000', 'condition': 'foreign_used',
            'transmission': 'automatic', 'fuel_type': 'petrol', 'body_type': 'sedan',
            'location': 'Ikeja, Lagos', 'status': 'available', 'is_active': 'on',
        }
        captured_files = {}

        from apps.admin_panel import views as admin_views
        original_validator = admin_views._validate_car_images

        def capture_files(uploaded_files):
            captured_files['files'] = list(uploaded_files)
            return original_validator(uploaded_files)

        with patch('apps.admin_panel.views._validate_car_images', side_effect=capture_files):
            response = self.client.post(
                create_url,
                {**post_data, 'images': [first, second]},
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            {uploaded.name for uploaded in captured_files['files']},
            {first.name, second.name},
        )
        car = Car.objects.get(make='Honda', model='Accord Sport')
        images = list(car.images.order_by('order'))
        self.assertEqual(len(images), 2)
        self.assertEqual([image.car_id for image in images], [car.id, car.id])
        self.assertTrue(images[0].is_cover)

        for image in images:
            self.assertTrue(image.image.name)
            self.assertTrue(default_storage.exists(image.image.name))
            with default_storage.open(image.image.name, 'rb') as stored_file:
                with Image.open(stored_file) as stored_image:
                    stored_image.verify()
            self.assertTrue(image.image.url.startswith('/media/'))

        edit_response = self.client.get(reverse('admin_panel:car_edit', args=[car.id]))
        public_response = self.client.get(reverse('cars:detail', args=[car.id]))
        for image in images:
            self.assertContains(edit_response, image.image.url)
            self.assertContains(public_response, image.image.url)

    def test_admin_edit_car_price_and_status(self):
        self.client.force_login(self.admin)
        edit_url = reverse('admin_panel:car_edit', args=[self.car1.id])
        post_data = {
            'make': 'Toyota',
            'model': 'Camry XSE',
            'year': '2021',
            'price': '23500000',
            'mileage': '32000',
            'condition': 'foreign_used',
            'transmission': 'automatic',
            'fuel_type': 'petrol',
            'body_type': 'sedan',
            'engine': '2.5L 4-Cylinder',
            'exterior_color': 'Midnight Black',
            'interior_color': 'Red Leather',
            'location': 'Lekki, Lagos',
            'status': 'sold',
            'is_featured': 'on',
            'is_active': 'on',
            'description': 'Updated description',
            'features': [self.f_ac.id]
        }
        response = self.client.post(edit_url, post_data)
        self.assertEqual(response.status_code, 302)

        # Verify DB updated
        self.car1.refresh_from_db()
        self.assertEqual(self.car1.price, Decimal("23500000"))
        self.assertEqual(self.car1.status, "sold")

        # Verify public view displays updated price & sold badge
        public_resp = self.client.get(reverse('cars:detail', args=[self.car1.id]))
        self.assertContains(public_resp, "23,500,000")
        self.assertContains(public_resp, "SOLD")

    def test_admin_edit_car_uploads_multiple_images_and_sets_first_cover(self):
        self.client.force_login(self.admin)
        edit_url = reverse('admin_panel:car_edit', args=[self.car1.id])
        initial_image_count = self.car1.images.count()
        front_name = f"front-regression-{uuid4().hex}.jpg"
        post_data = {
            'make': 'Toyota', 'model': 'Camry XSE', 'year': '2021',
            'price': '25000000', 'mileage': '32000', 'condition': 'foreign_used',
            'transmission': 'automatic', 'fuel_type': 'petrol', 'body_type': 'sedan',
            'engine': '2.5L 4-Cylinder', 'exterior_color': 'White',
            'interior_color': 'Black Leather', 'location': 'Lekki, Lagos',
            'status': 'available', 'is_active': 'on',
        }
        response = self.client.post(
            edit_url,
            {
                **post_data,
                'images': [
                    self._uploaded_image(front_name),
                    self._uploaded_image(f"side-regression-{uuid4().hex}.png", 'PNG'),
                ],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, edit_url)
        images = list(self.car1.images.order_by('order'))
        self.assertEqual(len(images), initial_image_count + 2)
        self.assertTrue(all(image.car_id == self.car1.id for image in images))
        self.assertTrue(images[0].is_cover)
        self.assertFalse(images[1].is_cover)
        self.assertTrue(images[0].image.name.startswith('cars/'))
        self.assertTrue(images[0].image.url.startswith('/media/'))
        self.assertEqual(
            images[0].image.name,
            f"cars/{timezone.now():%Y/%m}/{front_name}",
        )
        self.assertTrue(default_storage.exists(images[0].image.name))
        with default_storage.open(images[0].image.name, 'rb') as stored_file:
            with Image.open(stored_file) as stored_image:
                stored_image.verify()

        edit_response = self.client.get(response.url)
        self.assertEqual(edit_response.status_code, 200)
        self.assertContains(edit_response, images[0].image.url)
        self.assertContains(edit_response, images[1].image.url)
        self.assertNotContains(
            edit_response,
            '<img src="/static/images/car-fallback.svg"',
        )
        public_response = self.client.get(reverse('cars:detail', args=[self.car1.id]))
        self.assertContains(public_response, images[0].image.url)
        self.assertContains(public_response, images[1].image.url)

    def test_admin_edit_replaces_placeholder_cover_with_uploaded_image(self):
        placeholder = CarImage.objects.create(
            car=self.car1,
            image=SimpleUploadedFile(
                'placeholder.svg',
                b'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"></svg>',
                content_type='image/svg+xml',
            ),
            is_cover=True,
            order=0,
        )
        self.client.force_login(self.admin)
        edit_url = reverse('admin_panel:car_edit', args=[self.car1.id])
        response = self.client.post(
            edit_url,
            {
                'make': 'Toyota', 'model': 'Camry XSE', 'year': '2021',
                'price': '25000000', 'mileage': '32000', 'condition': 'foreign_used',
                'transmission': 'automatic', 'fuel_type': 'petrol', 'body_type': 'sedan',
                'location': 'Lekki, Lagos', 'status': 'available',
                'images': self._uploaded_image('toyota-real.jpg'),
            },
        )

        self.assertEqual(response.status_code, 302)
        uploaded_image = self.car1.images.exclude(pk=placeholder.pk).get()
        placeholder.refresh_from_db()
        self.assertTrue(uploaded_image.is_cover)
        self.assertFalse(placeholder.is_cover)
        self.assertTrue(Path(settings.MEDIA_ROOT, uploaded_image.image.name).is_file())
        edit_response = self.client.get(response.url)
        self.assertContains(edit_response, uploaded_image.image.url)
        self.assertNotContains(
            edit_response,
            '<img src="/static/images/car-fallback.svg"',
        )

    def test_admin_image_cover_selection_and_deletion(self):
        first = CarImage.objects.create(
            car=self.car1, image=self._uploaded_image('first.jpg'), is_cover=True, order=0
        )
        second = CarImage.objects.create(
            car=self.car1, image=self._uploaded_image('second.webp', 'WEBP'), order=1
        )
        self.client.force_login(self.admin)

        cover_response = self.client.get(
            reverse('admin_panel:car_image_set_cover', args=[second.id])
        )
        self.assertEqual(cover_response.status_code, 302)
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_cover)
        self.assertTrue(second.is_cover)
        self.assertEqual(self.car1.images.filter(is_cover=True).count(), 1)

        delete_response = self.client.get(
            reverse('admin_panel:car_image_delete', args=[first.id])
        )
        self.assertEqual(delete_response.status_code, 302)
        self.assertFalse(CarImage.objects.filter(pk=first.id).exists())
        self.assertTrue(CarImage.objects.filter(pk=second.id).exists())

    def test_admin_edit_rejects_invalid_car_image(self):
        self.client.force_login(self.admin)
        edit_url = reverse('admin_panel:car_edit', args=[self.car1.id])
        response = self.client.post(
            edit_url,
            {
                'make': 'Toyota', 'model': 'Camry XSE', 'year': '2021',
                'price': '25000000', 'mileage': '32000', 'condition': 'foreign_used',
                'transmission': 'automatic', 'fuel_type': 'petrol', 'body_type': 'sedan',
                'location': 'Lekki, Lagos', 'status': 'available',
                'images': SimpleUploadedFile(
                    'not-an-image.jpg', b'not an image', content_type='image/jpeg'
                ),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'not a valid JPEG, PNG, or WebP image')
        self.assertEqual(self.car1.images.count(), 0)

    def test_admin_delete_car(self):
        self.client.force_login(self.admin)
        car_to_delete = Car.objects.create(
            make="Ford",
            model="Edge",
            year=2019,
            price=Decimal("17000000"),
            mileage=50000,
            status="available"
        )
        delete_url = reverse('admin_panel:car_delete', args=[car_to_delete.id])
        # GET returns confirm page
        resp_get = self.client.get(delete_url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, "Confirm Vehicle Deletion")

        # POST performs deletion
        resp_post = self.client.post(delete_url)
        self.assertEqual(resp_post.status_code, 302)
        self.assertFalse(Car.objects.filter(id=car_to_delete.id).exists())

    def test_admin_status_and_featured_toggles(self):
        self.client.force_login(self.admin)
        # Toggle status to sold
        self.client.get(reverse('admin_panel:car_toggle_status', args=[self.car1.id, 'sold']))
        self.car1.refresh_from_db()
        self.assertEqual(self.car1.status, 'sold')

        # Toggle featured
        orig_featured = self.car1.is_featured
        self.client.get(reverse('admin_panel:car_toggle_featured', args=[self.car1.id]))
        self.car1.refresh_from_db()
        self.assertEqual(self.car1.is_featured, not orig_featured)

    # 7. Site Settings & Testimonials Management
    def test_admin_site_settings_update(self):
        self.client.force_login(self.admin)
        post_data = {
            'site_name': 'Samko Premium Motors',
            'tagline': 'Drive Your Dream in Lagos',
            'phone': '+234 800 000 1111',
            'whatsapp_number': '2348000001111',
            'email': 'sales@samkopremium.ng',
            'address': 'Plot 10, Admiralty Way, Lekki Phase 1',
            'city': 'Lagos, Nigeria',
            'opening_hours': 'Mon - Sat: 8am - 6pm',
            'hero_title': 'Luxury & Reliable Cars in Nigeria',
            'hero_subtitle': 'Verified vehicles with inspection warranty',
            'about_story': 'Samko Cars has been serving Nigerians since 2015.',
            'footer_text': 'All rights reserved Samko Cars.'
        }
        response = self.client.post(reverse('admin_panel:settings'), post_data)
        self.assertEqual(response.status_code, 302)
        
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.site_name, 'Samko Premium Motors')
        self.assertEqual(self.settings.whatsapp_number, '2348000001111')

    def test_testimonials_and_social_media(self):
        self.client.force_login(self.admin)
        # Add testimonial
        resp_test = self.client.post(reverse('admin_panel:testimonials'), {
            'action': 'add',
            'name': 'Chief Adeleke',
            'location': 'Victoria Island, Lagos',
            'vehicle_purchased': '2022 Mercedes GLE 450',
            'rating': '5',
            'comment': 'Smooth purchase experience. Car was delivered in immaculate condition.'
        })
        self.assertEqual(resp_test.status_code, 302)
        self.assertTrue(Testimonial.objects.filter(name='Chief Adeleke').exists())

        # Add social media
        resp_soc = self.client.post(reverse('admin_panel:social'), {
            'action': 'add',
            'platform': 'instagram',
            'platform_name': '@samkocars',
            'url': 'https://instagram.com/samkocars',
            'order': '1'
        })
        self.assertEqual(resp_soc.status_code, 302)
        self.assertTrue(SocialMedia.objects.filter(platform='instagram').exists())

    # 8. REST API Endpoints
    def test_rest_api_endpoint(self):
        response = self.client.get(reverse('cars:api_car_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertGreaterEqual(data['count'], 2)

    def test_rest_api_detail_endpoint(self):
        response = self.client.get(reverse('cars:api_car_detail', args=[self.car1.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['make'], 'Toyota')
        self.assertEqual(data['model'], 'Camry XSE')

    # 9. 404 Behavior
    def test_404_page(self):
        response = self.client.get('/cars/999999999/')
        self.assertEqual(response.status_code, 404)
