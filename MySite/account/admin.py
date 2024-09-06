from django.contrib import admin
from .models import CustomUser
from rest_framework.authtoken.models import Token
# Register your models here.

admin.site.register(CustomUser)

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created')
    search_fields = ('user__username', 'key')
    readonly_fields = ('key', 'created')