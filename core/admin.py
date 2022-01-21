from django.contrib import admin

# Register your models here.
from core.models import CompanyDetails, CompanySource, File, UploadDetails


@admin.register(CompanyDetails)
class CompanyDetailsAdmin(admin.ModelAdmin):
    list_display = ['_id', '_index', '_type', 'created_on']


@admin.register(CompanySource)
class CompanySourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'organization_name', 'organization_id']


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'json_file', 'start_processing_time', 'stop_processing_time', 'status', 'created_number',
                    'updated_number']


@admin.register(UploadDetails)
class UploadDetailsAdmin(admin.ModelAdmin):
    list_display = ['created_by', 'created_on']
