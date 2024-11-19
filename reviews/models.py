from django.db import models
from django.conf import settings
from posts.models import Post
from posts.models import RentRequest

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    rent_request = models.ForeignKey(RentRequest, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.renter} for {self.post}'
