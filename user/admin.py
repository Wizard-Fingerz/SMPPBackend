from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *
# Register your models here.

@admin.register(ProfileMedia)
class ProfileMediaAdmin(ImportExportModelAdmin):
    list_display = ('media',)


@admin.register(User)
class UsersAdmin(ImportExportModelAdmin):
    list_display = ('username', 'first_name', 'last_name','email','phone_number',
                    'is_business', 'is_personal', 'is_admin','is_verified')
    search_fields = ['username', 'first_name', 'last_name']
    list_editable = ['is_business', 'is_personal', 'is_admin',]
    list_filter = ('is_business', 'is_personal', 'is_admin','is_verified')


@admin.register(UserProfile)
class UserProfileAdmin(ImportExportModelAdmin):
    list_display = ('user','work', 'date_of_birth', 'gender',)
    list_filter = ('gender',)
    search_fields = ['user',]


@admin.register(ReportedUser)
class ReportedUserAdmin(ImportExportModelAdmin):
    list_display = ('user', 'is_banned', 'is_disabled')
    list_editable = ['is_banned', 'is_disabled',]

@admin.register(Address)
class AddressAdmin(ImportExportModelAdmin):
    list_display = ('country', 'city', 'location')


@admin.register(Notification)
class NotificationAdmin(ImportExportModelAdmin):
    list_display = ('recipient', 'sender', 'message', 'timestamp')


admin.site.site_header = 'SMPP Administration Dashboard'