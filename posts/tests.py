from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from posts.models import Post, RentRequest
from http import HTTPStatus

class PostAndBookingTest(TestCase):
    """
    Test suite per il sistema di prenotazione.
    """
    
    def setUp(self):
        """
        Configurazione iniziale per ogni test.
        Crea un utente proprietario (landlord) e un affittuario (renter).
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

        # Dati di base per un annuncio
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

    def test_landlord_create_post(self):
        """
        Verifica che un proprietario possa creare un nuovo annuncio.
        Il test controlla:
        - La corretta autenticazione
        - La creazione dell'annuncio nel database
        - La correttezza dei dati salvati
        """
        # Login come proprietario
        self.client.login(email="landlord@example.com", password="password123")
        
        # Invia richiesta POST per creare l'annuncio
        response = self.client.post(reverse('post_create'), self.post_data)
        
        # Verifica il redirect dopo la creazione (status code 302)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Verifica che l'annuncio sia stato creato
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.title, "Appartamento con giardino")
        self.assertEqual(post.landlord, self.landlord)

    def test_renter_create_booking(self):
        """
        Verifica che un affittuario possa creare una richiesta di prenotazione.
        Il test controlla:
        - La presenza di un annuncio valido
        - La corretta creazione della richiesta
        - Lo stato iniziale della richiesta
        """
        # Crea prima un annuncio come proprietario
        self.client.login(email="landlord@example.com", password="password123")
        self.client.post(reverse('post_create'), self.post_data)
        self.client.logout()
        
        # Login come affittuario
        self.client.login(email="renter@example.com", password="password123")
        
        # Prepara i dati per la prenotazione
        post = Post.objects.first()
        booking_data = {
            'start_date': (timezone.now() + timedelta(days=1)).date(),
            'end_date': (timezone.now() + timedelta(days=4)).date(),
        }
        
        # Invia la richiesta di prenotazione
        response = self.client.post(
            reverse('rent_request_create', kwargs={'post_id': post.id}),
            booking_data
        )
        
        # Verifica il redirect dopo la creazione
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Verifica la creazione della richiesta
        rent_request = RentRequest.objects.first()
        self.assertIsNotNone(rent_request)
        self.assertEqual(rent_request.status, 'pending')
        self.assertEqual(rent_request.renter, self.renter)

    def test_landlord_approve_request(self):
        """
        Verifica che un proprietario possa approvare una richiesta di prenotazione.
        Il test controlla:
        - La corretta approvazione della richiesta
        - L'aggiornamento dello stato
        """
        # Crea un annuncio e una richiesta di prenotazione
        self._create_post_and_booking()
        
        # Login come proprietario
        self.client.login(email="landlord@example.com", password="password123")
        
        # Approva la richiesta
        rent_request = RentRequest.objects.first()
        response = self.client.get(
            reverse('approve_rent_request', kwargs={'pk': rent_request.id})
        )
        
        # Verifica il redirect
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Verifica che lo stato sia cambiato
        rent_request.refresh_from_db()
        self.assertEqual(rent_request.status, 'approved')

    def test_landlord_reject_request(self):
        """
        Verifica che un proprietario possa rifiutare una richiesta di prenotazione.
        Il test controlla:
        - Il corretto rifiuto della richiesta
        - L'aggiornamento dello stato
        """
        # Crea un annuncio e una richiesta di prenotazione
        self._create_post_and_booking()
        
        # Login come proprietario
        self.client.login(email="landlord@example.com", password="password123")
        
        # Rifiuta la richiesta
        rent_request = RentRequest.objects.first()
        response = self.client.get(
            reverse('reject_rent_request', kwargs={'pk': rent_request.id})
        )
        
        # Verifica il redirect
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Verifica che lo stato sia cambiato
        rent_request.refresh_from_db()
        self.assertEqual(rent_request.status, 'rejected')

    def _create_post_and_booking(self):
        """
        Metodo di utilità per creare un annuncio e una prenotazione.
        Utilizzato dai test di approvazione e rifiuto.
        """
        # Crea l'annuncio
        self.client.login(email="landlord@example.com", password="password123")
        self.client.post(reverse('post_create'), self.post_data)
        self.client.logout()
        
        # Crea la prenotazione
        self.client.login(email="renter@example.com", password="password123")
        post = Post.objects.first()
        booking_data = {
            'start_date': (timezone.now() + timedelta(days=1)).date(),
            'end_date': (timezone.now() + timedelta(days=4)).date(),
        }
        self.client.post(
            reverse('rent_request_create', kwargs={'post_id': post.id}),
            booking_data
        )
        self.client.logout()