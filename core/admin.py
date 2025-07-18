from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product, Land, Input, Service, Video

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_email_verified', 'is_staff', 'is_active')
    list_filter = ('is_email_verified', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Verification', {'fields': ('is_email_verified', 'verification_code')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_email_verified'),
        }),
    )

# Product Admin with improved display
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'price', 'quantity', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'

# Land Admin
class LandAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'location', 'price', 'size', 'is_for_sale', 'created_at')
    list_filter = ('is_for_sale', 'created_at')
    search_fields = ('title', 'description', 'location', 'user__username')
    raw_id_fields = ('user',)

# Input Admin
class InputAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'price', 'quantity', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    list_filter = ('created_at',)
    raw_id_fields = ('user',)

# Service Admin
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'location', 'price', 'created_at')
    search_fields = ('title', 'description', 'location', 'user__username')
    list_filter = ('created_at',)
    raw_id_fields = ('user',)

# Video Admin
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'youtube_video_id', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    list_filter = ('created_at',)
    raw_id_fields = ('user',)

# Register your models here
admin.site.register(User, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Land, LandAdmin)
admin.site.register(Input, InputAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Video, VideoAdmin)