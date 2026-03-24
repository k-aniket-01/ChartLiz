from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'experience_level', 'timezone', 'dark_mode', 'is_staff')
    list_filter = ('experience_level', 'dark_mode', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    
    # Add our custom fields to the edit form
    fieldsets = UserAdmin.fieldsets + (
        ('ChartLiz Profile', {
            'fields': ('experience_level', 'avatar', 'timezone', 'dark_mode')
        }),
    )
    
    # Add our custom fields to the add (create) form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('ChartLiz Profile', {
            'fields': ('experience_level', 'avatar', 'timezone', 'dark_mode')
        }),
    )