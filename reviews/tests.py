from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from posts.models import Post, RentRequest
from reviews.models import Review
from http import HTTPStatus


class ReviewTest(TestCase):
    """
    Test suite per la creazione delle recensioni.
    """

    def setUp(self):
        """
        Configurazione iniziale per ogni test.
        Crea un utente proprietario (landlord), un affittuario (renter) e un post.
        """
        # Creazione dell'utente proprietario
        self.landlord = get_user_model().objects.create_user(
            email="landlord@example.com",
            password="password123",
            user_type="landlord",
            name="John",
            surname="Doe"
        )

        # Creazione dell'utente affittuario
        self.renter = get_user_model().objects.create_user(
            email="renter@example.com",
            password="password123",
            user_type="renter",
            name="Jane",
            surname="Doe"
        )

        # Creazione di un post
        self.post_data = {
            'title': "Appartamento con giardino",
            'description': "Un bel posto con un giardino spazioso.",
            'address': "Via Verde 123, Springtown",
            'wifi': True,
            'bathroom': True,
            'bbq': False,
            'pool': True,
            'kid_friendly': True,
            'parking': True,
            'electricity': True,
            'max_people': 4,
            'price_per_person': 120.00
        }

        # Creiamo un post come proprietario
        self.client.login(email="landlord@example.com", password="password123")
        self.client.post(reverse('post_create'), self.post_data)
        self.client.logout()

        # Crea una RentRequest approvata per l'affittuario
        self.client.login(email="renter@example.com", password="password123")
        post = Post.objects.first()
        rent_request_data = {
            'start_date': (timezone.now() + timedelta(days=1)).date(),
            'end_date': (timezone.now() + timedelta(days=4)).date(),
        }
        self.client.post(reverse('rent_request_create', kwargs={'post_id': post.id}), rent_request_data)
        
        # Approva la RentRequest
        rent_request = RentRequest.objects.first()
        rent_request.status = 'approved'
        rent_request.save()
        self.client.logout()

    def test_create_review(self):
        """
        Verifica che un affittuario possa creare una recensione per una richiesta di prenotazione approvata.
        """
        # Verifica che l'utente sia loggato come affittuario
        self.client.login(email="renter@example.com", password="password123")
        
        # Prepara i dati per la recensione
        review_data = {
            'rating': 5,
            'review_text': "Un'esperienza fantastica, appartamento perfetto!"
        }

        # Ottieni la RentRequest approvata
        rent_request = RentRequest.objects.filter(status='approved').first()

        # Invia la recensione per la richiesta di prenotazione
        response = self.client.post(
            reverse('review_create', kwargs={'rent_request_id': rent_request.id}),
            review_data
        )

        # Verifica il redirect dopo la creazione della recensione
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Verifica che la recensione sia stata creata nel database
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()

        # Verifica che la recensione sia associata al corretto affittuario, annuncio e richiesta
        self.assertEqual(review.renter, self.renter)
        self.assertEqual(review.post, rent_request.post)
        self.assertEqual(review.rent_request, rent_request)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review_text, "Un'esperienza fantastica, appartamento perfetto!")

    def test_cannot_create_review_for_non_approved_rent_request(self):
        """
        Verifica che non sia possibile creare una recensione per una richiesta di prenotazione non approvata.
        """
        # Crea una RentRequest non approvata per l'affittuario
        self.client.login(email="renter@example.com", password="password123")
        post = Post.objects.first()
        rent_request_data = {
            'start_date': (timezone.now() + timedelta(days=1)).date(),
            'end_date': (timezone.now() + timedelta(days=4)).date(),
        }
        self.client.post(reverse('rent_request_create', kwargs={'post_id': post.id}), rent_request_data)
        
        # Non approvare la RentRequest
        rent_request = RentRequest.objects.last()
        rent_request.status = 'pending'
        rent_request.save()
        self.client.logout()

        # Prova a creare una recensione per una RentRequest non approvata
        self.client.login(email="renter@example.com", password="password123")
        rent_request = RentRequest.objects.filter(status='pending').first()
        review_data = {
            'rating': 4,
            'review_text': "Appartamento ok, ma con alcuni problemi."
        }

        # Tentiamo di inviare una recensione per la RentRequest non approvata
        response = self.client.post(
            reverse('review_create', kwargs={'rent_request_id': rent_request.id}),
            review_data
        )

        # Verifica che non sia stato possibile creare la recensione
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_review_for_multiple_rent_requests(self):
        """
        Verifica che un affittuario possa creare recensioni per più richieste di prenotazione approvate.
        """
        # Crea due RentRequest approvate per lo stesso affittuario
        self.client.login(email="renter@example.com", password="password123")
        post = Post.objects.first()
        
        # Prima RentRequest
        rent_request_data_1 = {
            'start_date': (timezone.now() + timedelta(days=1)).date(),
            'end_date': (timezone.now() + timedelta(days=4)).date(),
        }
        self.client.post(reverse('rent_request_create', kwargs={'post_id': post.id}), rent_request_data_1)
        
        # Seconda RentRequest
        rent_request_data_2 = {
            'start_date': (timezone.now() + timedelta(days=5)).date(),
            'end_date': (timezone.now() + timedelta(days=8)).date(),
        }
        self.client.post(reverse('rent_request_create', kwargs={'post_id': post.id}), rent_request_data_2)

        # Approva entrambe le RentRequest
        rent_request_1 = RentRequest.objects.first()
        rent_request_1.status = 'approved'
        rent_request_1.save()

        rent_request_2 = RentRequest.objects.last()
        rent_request_2.status = 'approved'
        rent_request_2.save()

        self.client.logout()

        # Prova a creare due recensioni, una per ogni RentRequest
        self.client.login(email="renter@example.com", password="password123")

        # Prima recensione
        review_data_1 = {
            'rating': 5,
            'review_text': "Appartamento fantastico!"
        }
        response_1 = self.client.post(
            reverse('review_create', kwargs={'rent_request_id': rent_request_1.id}),
            review_data_1
        )

        # Seconda recensione
        review_data_2 = {
            'rating': 4,
            'review_text': "Buon soggiorno, ma un po' rumoroso."
        }
        response_2 = self.client.post(
            reverse('review_create', kwargs={'rent_request_id': rent_request_2.id}),
            review_data_2
        )

        # Verifica che entrambe le recensioni siano state create correttamente
        self.assertEqual(response_1.status_code, HTTPStatus.FOUND)
        self.assertEqual(response_2.status_code, HTTPStatus.FOUND)

        self.assertEqual(Review.objects.count(), 2)

