from django.db import models

class Media(models.Model):
    url = models.URLField(max_length=500)
    webp_url = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.url
    

