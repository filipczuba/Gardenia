from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.conf import settings
import os
import shutil

def user_profile_directory_path(instance, filename):
    sanitized_email = instance.email.replace('@', '_').replace('.', '_')
    return f'users/{sanitized_email}/{filename}'

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('landlord', 'Landlord'),
        ('renter', 'Renter'),
    ]
    
    
    username = None
    name = models.CharField(max_length=30, blank=True)
    surname = models.CharField(max_length=30, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='renter')
    address = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=400, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_directory_path, default='assets/default_user.png')

    
    email = models.EmailField(unique=True)

    #
    objects = CustomUserManager()

    
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'user_type']  # Fields required during user creation

    # Add related_name for reverse access to groups and user_permissions to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set', 
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        
        return f"{self.name} {self.surname} ({self.email})" if self.name and self.surname else self.email

    def save(self, *args, **kwargs):
        # Metodo di salvataggio modificato per salvare anche la propic
        if not self.pk: 
            super().save(*args, **kwargs)
            if self.profile_picture and self.profile_picture.name.startswith('users/temp/'):
                new_path = user_profile_directory_path(self, self.profile_picture.name.split('/')[-1])
                self.profile_picture.name = new_path
                super().save(*args, **kwargs)
        else:
            old_instance = CustomUser.objects.get(pk=self.pk)
            if old_instance.profile_picture and old_instance.profile_picture != self.profile_picture:
                old_instance.profile_picture.delete(save=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Metodo che elimina la propic quando il profilo è eliminato
        if self.profile_picture:
            self.profile_picture.delete(save=False)
        directory = os.path.join(settings.MEDIA_ROOT, f'users/{self.email.replace("@", "_").replace(".", "_")}')
        if os.path.exists(directory) and not os.listdir(directory):
            shutil.rmtree(directory)
        super().delete(*args, **kwargs)
