from django.contrib import admin
from frontend.models import Profile

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'public_key', 'secret_key')