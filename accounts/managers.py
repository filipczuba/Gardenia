from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # Ensure email is provided
        if not email:
            raise ValueError('La Mail deve essere fornita!')
        
        # Normalize the email
        email = self.normalize_email(email)
        
        # Create the user instance
        user = self.model(email=email, **extra_fields)
        
        # Set the user's password (will be hashed)
        user.set_password(password)
        
        # Save the user to the database
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Set the necessary fields for a superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Make sure the superuser is both staff and superuser
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Ensure required fields (like name and surname) are set
        extra_fields.setdefault('user_type', 'landlord')  # Default user_type for superuser
        extra_fields.setdefault('name', 'Admin')
        extra_fields.setdefault('surname', 'Superuser')

        # Call the create_user method to actually create the user
        return self.create_user(email, password, **extra_fields)
