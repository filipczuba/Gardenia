from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import UserProfileRegistrationForm, UserProfileForm

# Funzione per la registrazione di un nuovo utente
def register(request):
    # Reindirizza l'utente alla home se è già autenticato
    if request.user.is_authenticated:
        return redirect('home')  # Se l'utente è già loggato, reindirizza alla home

    # Gestisce la richiesta POST per la registrazione dell'utente
    if request.method == 'POST':
        form = UserProfileRegistrationForm(request.POST)

        # Valida il modulo
        if form.is_valid():
            user = form.save()  # Salva l'utente nel database
            print("Il modulo è valido. Reindirizzamento alla home...")
            login(request, user)  # Logga l'utente subito dopo la registrazione
            return redirect('home')  # Reindirizza alla home o ad un'altra pagina
    else:
        form = UserProfileRegistrationForm()  # Inizializza un modulo vuoto per le richieste GET

    # Renderizza il modulo di registrazione con eventuali errori se non è valido
    return render(request, 'accounts/register.html', {'form': form})

# Funzione per il logout dell'utente, disponibile solo per gli utenti autenticati
@login_required
def user_logout(request):
    logout(request)  # Esegue il logout dell'utente
    return redirect('login')  # Reindirizza alla pagina di login

# Funzione per modificare il profilo utente, disponibile solo per gli utenti autenticati
@login_required
def edit_profile(request):
    # Gestisce la richiesta POST per aggiornare i dati del profilo
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()  # Salva le modifiche al profilo
            return redirect('home')  # Reindirizza alla home o alla pagina del profilo
    else:
        form = UserProfileForm(instance=request.user)  # Carica i dati esistenti dell'utente nel modulo
    return render(request, 'accounts/edit_profile.html', {'form': form})
