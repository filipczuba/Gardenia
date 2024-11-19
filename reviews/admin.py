from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('renter', 'post', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'post')
    search_fields = ('review_text', 'renter__username', 'post__title')
    readonly_fields = ('created_at',)  

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('renter', 'post', 'rent_request', 'created_at')
        return super().get_readonly_fields(request, obj)
    
    def save_model(self, request, obj, form, change):
        if not change: 
            obj.renter = request.user
        super().save_model(request, obj, form, change)
