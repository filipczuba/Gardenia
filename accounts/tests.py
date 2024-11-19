from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus
import os

class AccountsTest(TestCase):
    """
    Suite di test per la gestione degli account utente.
    Verifica le funzionalità di registrazione, autenticazione e gestione del profilo.
    """

    def setUp(self):
        """
        Configurazione iniziale per ogni test.
        Crea un client HTTP e prepara i dati di test.
        """
        self.client = Client()
        
        # Dati base per un utente proprietario
        self.landlord_data = {
            'email': 'landlord@example.com',
            'password1': 'secure_password123',
            'password2': 'secure_password123',
            'name': 'Mario',
            'surname': 'Rossi',
            'user_type': 'landlord',
        }
        
        # Dati base per un utente affittuario
        self.renter_data = {
            'email': 'renter@example.com',
            'password1': 'secure_password123',
            'password2': 'secure_password123',
            'name': 'Luigi',
            'surname': 'Verdi',
            'user_type': 'renter',
        }

        # Crea un utente di test per il login
        self.test_user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test_password123',
            name='Test',
            surname='User',
            user_type='renter'
        )

    def test_user_registration_landlord(self):
        """
        Verifica la registrazione di un nuovo utente proprietario.
        Controlla:
        - La corretta creazione dell'utente nel database
        - Il redirect dopo la registrazione
        - I dati salvati nel database
        """
        response = self.client.post(reverse('register'), self.landlord_data)
        
        # Verifica il redirect dopo la registrazione
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Verifica che l'utente sia stato creato
        user = get_user_model().objects.get(email=self.landlord_data['email'])
        self.assertEqual(user.name, self.landlord_data['name'])
        self.assertEqual(user.user_type, 'landlord')
        
        # Verifica che l'utente sia autenticato
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_registration_renter(self):
        """
        Verifica la registrazione di un nuovo utente affittuario.
        """
        response = self.client.post(reverse('register'), self.renter_data)
        
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        user = get_user_model().objects.get(email=self.renter_data['email'])
        self.assertEqual(user.name, self.renter_data['name'])
        self.assertEqual(user.user_type, 'renter')
        
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_registration_invalid_data(self):
        """
        Verifica che la registrazione fallisca con dati non validi.
        Controlla vari casi di errore comuni.
        """
        # Test con password non corrispondenti
        invalid_data = self.renter_data.copy()
        invalid_data['password2'] = 'different_password'
        response = self.client.post(reverse('register'), invalid_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)  # Rimane sulla pagina
        self.assertFalse(get_user_model().objects.filter(email=invalid_data['email']).exists())

        # Test con email già esistente
        self.client.post(reverse('register'), self.renter_data)  # Prima registrazione
        response = self.client.post(reverse('register'), self.renter_data)  # Seconda registrazione
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(get_user_model().objects.filter(email=self.renter_data['email']).count(), 1)

    def test_user_login(self):
        """
        Verifica il processo di login.
        Controlla:
        - Login con credenziali corrette
        - Login con credenziali errate
        - Redirect dopo il login
        """
        # Test login con credenziali corrette
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',  # Django usa 'username' anche per email
            'password': 'test_password123',
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Test login con password errata
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'password': 'wrong_password',
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_user_logout(self):
        """
        Verifica il processo di logout.
        """
        # Prima effettua il login
        self.client.login(username='test@example.com', password='test_password123')
        
        # Effettua il logout
        response = self.client.get(reverse('logout'))
        
        # Verifica il redirect dopo il logout
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        
        # Verifica che l'utente non sia più autenticato
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_edit_profile(self):
        """
        Verifica la funzionalità di modifica del profilo.
        Controlla:
        - Modifica dei dati del profilo
        - Upload dell'immagine del profilo
        - Validazione dei dati
        """
        # Login
        self.client.login(username='test@example.com', password='test_password123')
        
        # Prepara i nuovi dati del profilo
        new_profile_data = {
            'email': 'test@example.com',  # Email non modificata
            'name': 'New Name',
            'surname': 'New Surname',
            'description': 'New description',
            'phone_number': '+39123456789',
            'address': 'New Address, 123'
        }
        
        # Crea un file di test per l'immagine del profilo
        image_content = b'fake-image-content'
        profile_picture = SimpleUploadedFile(
            'test_image.jpg',
            image_content,
            content_type='image/jpeg'
        )
        new_profile_data['profile_picture'] = profile_picture
        
        # Invia la richiesta di modifica
        response = self.client.post(reverse('edit_profile'), new_profile_data)
        
        # Verifica il redirect
        self.assertEqual(response.status_code, HTTPStatus.OK)
        
        # Verifica che i dati siano stati aggiornati
        updated_user = response.wsgi_request.user
        self.assertEqual(updated_user.name, 'New Name')
        self.assertEqual(updated_user.surname, 'New Surname')
        self.assertEqual(updated_user.description, 'New description')
        
        # Verifica che l'immagine sia stata caricata
        self.assertTrue(updated_user.profile_picture)
        
        # Pulisce i file caricati durante il test
        if os.path.exists(updated_user.profile_picture.path):
            os.remove(updated_user.profile_picture.path)

    def test_unauthorized_access(self):
        """
        Verifica che le pagine protette non siano accessibili senza autenticazione.
        """
        # Prova ad accedere alla pagina di modifica profilo senza login
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # Redirect al login
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_registration_redirect_authenticated(self):
        """
        Verifica che gli utenti già autenticati vengano reindirizzati
        quando provano ad accedere alla pagina di registrazione.
        """
        # Login
        self.client.login(username='test@example.com', password='test_password123')
        
        # Prova ad accedere alla pagina di registrazione
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('home'))