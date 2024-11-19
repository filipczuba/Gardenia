# posts/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView ,DetailView ,View
from django.db.models import Q
from .models import Post, RentRequest
from .forms import PostForm, RentRequestForm
from reviews.models import Review
from django.contrib import messages
from accounts.models import CustomUser

# Landlord's view to list their properties
class LandlordPropertiesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Post
    template_name = 'posts/landlord_properties.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(landlord=self.request.user)

    def test_func(self):
        return self.request.user.user_type == 'landlord'

# Landlord's view to list their received rent requests
class LandlordRentRequestsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = RentRequest
    template_name = 'posts/landlord_rent_requests.html'
    context_object_name = 'rent_requests'

    def get_queryset(self):
        return RentRequest.objects.filter(post__landlord=self.request.user)

    def test_func(self):
        return self.request.user.user_type == 'landlord'

# Renter's view to list their bookings
class RenterBookingsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = RentRequest
    template_name = 'posts/renter_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return RentRequest.objects.filter(renter=self.request.user)

    def test_func(self):
        return self.request.user.user_type == 'renter'

class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('home')  # Change to the name of your home URL

    def form_valid(self, form):
        form.instance.landlord = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.user_type == 'landlord'

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('home')  # Change to the name of your home URL

    def form_valid(self, form):
        return super().form_valid(form)

    def get_queryset(self):
        return Post.objects.filter(landlord=self.request.user)

    def test_func(self):
        post = self.get_object()
        return post.landlord == self.request.user

# Deleting a post (only by the landlord)
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('landlord_properties')

    def get_queryset(self):
        return Post.objects.filter(landlord=self.request.user)

    def test_func(self):
        post = self.get_object()
        return post.landlord == self.request.user

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

class RentRequestCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = RentRequest
    form_class = RentRequestForm
    template_name = 'posts/rent_request_form.html'
    success_url = reverse_lazy('renter_bookings')

    def form_valid(self, form):
        form.instance.renter = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        
        # Check general availability of the post
        if form.instance.post.is_available(form.instance.start_date, form.instance.end_date):
            return super().form_valid(form)
        else:
            # Add non-field error to the form
            form.add_error(None, "Questa proprietà è già stata prenotata in questo periodo.")
            return self.form_invalid(form)  # This will ensure the form is re-rendered with the error

    def test_func(self):
        return self.request.user.user_type == 'renter'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return context


# Displaying properties on home page


class HomeView(ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = Post.objects.all()

        # Query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(address__icontains=query)
            )

        # Filtra numero minimo di persone
        min_people = self.request.GET.get('min_people')
        if min_people:
            queryset = queryset.filter(max_people__gte=min_people)

        #Filtro costo massimo
        max_price = self.request.GET.get('max_price')
        if max_price:
            queryset = queryset.filter(price_per_person__lte=max_price)

        # Filtro tags
        tags = self.request.GET.getlist('tags')
        if tags:
            tag_filter = Q()
            for tag in tags:
                if tag == '1':
                    tag_filter |= Q(wifi=True)
                elif tag == '2':
                    tag_filter |= Q(bathroom=True)
                elif tag == '3':
                    tag_filter |= Q(bbq=True)
                elif tag == '4':
                    tag_filter |= Q(pool=True)
                elif tag == '5':
                    tag_filter |= Q(kid_friendly=True)
                elif tag == '6':
                    tag_filter |= Q(parking=True)
                elif tag == '7':
                    tag_filter |= Q(electricity=True)
            queryset = queryset.filter(tag_filter)

        return queryset


class RentRequestActionView(LoginRequiredMixin, UserPassesTestMixin, View):
    action = None  # 'approve', 'reject'

    def get(self, request, *args, **kwargs):
        rent_request = get_object_or_404(RentRequest, id=kwargs['pk'])
        post = rent_request.post  # Associato al post

        if self.action == 'approve':
            
            # Controllo dell'accavallamento delle data
            conflicting_request = RentRequest.objects.filter(
                post=post, 
                status='approved'
            ).filter(
                
                start_date__lt=rent_request.end_date, 
                end_date__gt=rent_request.start_date
            ).exists()

            if conflicting_request:
                
                messages.error(request, "Non puoi accettare questa richiesta, in quanto è già stata prenotata in un periodo sovrapponibile.")
                return redirect('landlord_rent_requests') 

   
            rent_request.status = 'approved'

        elif self.action == 'reject':
            rent_request.status = 'rejected'

        
        rent_request.save()

        return redirect('landlord_rent_requests')  #SI RITORNA AL PANNELLO DI CONTROLLO DEL LANDLORD

    def test_func(self):
        rent_request = get_object_or_404(RentRequest, id=self.kwargs['pk'])
        return self.request.user == rent_request.post.landlord and self.request.user.user_type == 'landlord'




class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rent_requests'] = self.object.rent_requests.all() 
        context['reviews'] = Review.objects.filter(post=self.object)  # Prendi le recensioni al post
        return context