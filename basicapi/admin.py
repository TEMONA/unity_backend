from django.contrib import admin
from .models import User, Profile, UserActivateTokens
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    ordering = ('id',)
    list_display = ('email', 'id', 'is_active', 'password', 'kaonavi_code')
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Personal Information', {'fields': ('username', 'kaonavi_code')}),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',),
        }),
    )
    inlines = (ProfileInline,)

class ProfileAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ('__str__', 'user', 'tweet', 'from_last_login', 'created_at')

class UserActivateTokensAdmin(admin.ModelAdmin):
    list_display = ('token_id', 'user', 'activate_token', 'expired_at')

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(UserActivateTokens, UserActivateTokensAdmin)
