from django.contrib import admin
from .models import Post, RentRequest
from django import forms
from accounts.models import CustomUser

class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['landlord'].queryset = CustomUser.objects.filter(user_type='landlord')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    readonly_fields=("id",)
    list_display = ('title', 'landlord', 'address', 'created_at')
    search_fields = ('title', 'landlord__user__username', 'address')
    list_filter = ('created_at',)

@admin.register(RentRequest)
class RentRequestAdmin(admin.ModelAdmin):
    list_display = ('post', 'renter', 'start_date', 'end_date', 'status')
    search_fields = ('post__title', 'renter__user__username')
    list_filter = ('status', 'start_date', 'end_date')