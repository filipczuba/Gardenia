# posts/models.py
from django.conf import settings
from django.db import models
from django.urls import reverse_lazy
import os
import shutil


def post_image_directory_path(instance, filename):
    email = instance.landlord.email.replace('@', '_').replace('.', '_')
    return f'posts/{email}/{filename}'


class Post(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=255)
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Tags as boolean fields
    wifi = models.BooleanField(default=False)
    bathroom = models.BooleanField(default=False)
    bbq = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    kid_friendly = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    electricity = models.BooleanField(default=False)


    max_people = models.PositiveIntegerField(default=20)  # Default 20
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, null=False,default=100) 

    image = models.ImageField(upload_to='posts/', default='assets/logo_greyscale.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    

    def get_absolute_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.pk})
    
    def is_available(self, start_date, end_date):
        #COntrolla che non ci siano richieste gia approvate nello stesso periodo
        overlapping_requests = RentRequest.objects.filter(
            post=self,
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        return not overlapping_requests.exists()

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            # Aggiorna l'immagine se necessario
            if self.image and self.image.name.startswith('posts/temp/'):
                new_path = self.get_image_upload_path(self.image.name.split('/')[-1])
                self.image.name = new_path
                super().save(*args, **kwargs)
        else:
            old_instance = Post.objects.get(pk=self.pk)
            if old_instance.image and old_instance.image != self.image:
                old_instance.image.delete(save=False)
        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        # Se la cartella e' vuota viene elimintata
        directory = os.path.join(settings.MEDIA_ROOT, f'posts/{self.landlord.email.replace("@", "_").replace(".", "_")}')
        if os.path.exists(directory) and not os.listdir(directory):
            shutil.rmtree(directory)
        super().delete(*args, **kwargs)

    def get_image_upload_path(self, filename):
        return f'posts/{self.landlord.email.replace("@", "_").replace(".", "_")}/{self.pk}/{filename}'



class RentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='rent_requests')
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f'Rent Request by {self.renter} for {self.post}'
