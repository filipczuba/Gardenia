# reviews/views.py

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404,render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from posts.models import Post
from .models import Review
from posts.models import RentRequest
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm, ReviewEditForm

class ReviewablePostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'reviews/reviewable_posts.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        user = self.request.user
        # Richieste approvate e non ancora recensite
        rent_requests = RentRequest.objects.filter(
            renter=user, 
            status='approved'
        ).exclude(id__in=Review.objects.filter(renter=user).values_list('rent_request_id', flat=True))
        # Post legati a questa richiesta
        return Post.objects.filter(rent_requests__in=rent_requests).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        rent_requests = RentRequest.objects.filter(
            renter=user, 
            status='approved'
        ).exclude(id__in=Review.objects.filter(renter=user).values_list('rent_request_id', flat=True))
       
        context['rent_requests'] = rent_requests
        return context
    

class LandlordReviewsView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'reviews/landlord_reviews.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        return Review.objects.filter(post__landlord=self.request.user)


class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['rent_request_id'] = self.kwargs['rent_request_id']
        kwargs['renter'] = self.request.user
        return kwargs

    def form_valid(self, form):
        rent_request = get_object_or_404(RentRequest, pk=self.kwargs['rent_request_id'])
        form.instance.renter = self.request.user
        form.instance.rent_request = rent_request
        form.instance.post = rent_request.post  
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home') 
    
    
@login_required
def user_reviews(request):
    # Tutte le recensioni dell'utente attuale
    reviews = Review.objects.filter(renter=request.user).order_by('-created_at')
    return render(request, 'reviews/user_reviews.html', {'reviews': reviews})

@login_required
def landlord_reviews(request):
    # Tutte le recensioni delle proprietà del landlord attuale
    posts = Post.objects.filter(landlord=request.user)

    reviews = Review.objects.filter(post__in=posts).order_by('-created_at')
    return render(request, 'reviews/landlord_reviews.html', {'reviews': reviews})

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, renter=request.user)
    if request.method == 'POST':
        form = ReviewEditForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('user_reviews')
    else:
        form = ReviewEditForm(instance=review)
    return render(request, 'reviews/edit_review.html', {'form': form})

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
   
    if review.renter != request.user:
        return HttpResponseForbidden("You are not allowed to delete this review.")
    
    if request.method == 'POST':
        review.delete()
        return redirect('user_reviews') 
    return render(request, 'reviews/confirm_delete.html', {'review': review})