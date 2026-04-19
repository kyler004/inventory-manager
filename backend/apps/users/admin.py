from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import User, Role

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'role', 'location', 'is_active')
    
    def save_model(self, request, obj, form, change):
        # Hash the password if it's new or changed (and not already hashed text)
        if obj.password and not obj.password.startswith('pbkdf2_'):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Role)
