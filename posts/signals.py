# posts/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Tag

TAGS_CHOICES = [
    ('wifi', 'WiFi'),
    ('bathroom', 'Bathroom'),
    ('bbq', 'BBQ'),
    ('pool', 'Pool'),
    ('kid_friendly', 'Kid Friendly'),
    ('parking', 'Parking Nearby'),
    ('electricity', 'Electricity'),
]

@receiver(post_migrate)
def create_default_tags(sender, **kwargs):
    if sender.name == 'posts':  
        existing_tags = set(Tag.objects.values_list('name', flat=True))
        for tag_key, tag_value in TAGS_CHOICES:
            if tag_key not in existing_tags:
                Tag.objects.create(name=tag_key)
