from django.contrib import admin

from accounts.models import Profile


@admin.register(Profile)
class CompanySourceAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']
