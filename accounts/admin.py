from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser 

class CustomUserAdmin(UserAdmin):
    #
    list_display = ['email', 'name', 'surname', 'get_user_type', 'is_staff']
    
   
    search_fields = ['email', 'name', 'surname']
    
    
    ordering = ['email']

    # This method is used to display the user type in the list view
    def get_user_type(self, instance):
        return instance.user_type
    get_user_type.short_description = 'User Type'

    # Define the fieldsets for the change form (admin view when editing users)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'surname', 'user_type', 'address', 'description', 'phone_number', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Define the add_fieldsets for the create form (admin view when adding new users)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
        ('Profile Info', {
            'classes': ('wide',),
            'fields': ('name', 'surname', 'user_type', 'address', 'description', 'phone_number')}
        ),
    )

# Register the CustomUser model with the custom admin
admin.site.register(CustomUser, CustomUserAdmin)
