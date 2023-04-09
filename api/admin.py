from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'phone_number', 'company_name', 'job_title')
    list_filter = ('tier',)
    search_fields = ('user__username', 'user__email', 'company_name', 'job_title')

admin.site.register(UserProfile, UserProfileAdmin)
