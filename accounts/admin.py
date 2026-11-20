# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SiteSetting, Ticket, TicketMessage


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['phone_number', 'first_name', 'last_name', 'points', 'rivalry_wins', 'is_approved', 'is_staff']
    list_filter = ['is_approved', 'is_staff', 'university_name']
    list_editable = ['points', 'is_approved']
    search_fields = ['phone_number', 'first_name', 'last_name', 'student_id']
    ordering = ['-points']
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'email', 'avatar', 'student_id', 'university_name', 'field_of_study')
        }),
        ('آمار و امتیازات', {
            'fields': ('points', 'level', 'success_rate', 'rivalry_wins', 'rivalry_losses')
        }),
        ('دسترسی‌ها', {
            'fields': ('is_active', 'is_approved', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'is_staff', 'is_approved'),
        }),
    )


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('sender_type', 'sender', 'message', 'created_at')
    can_delete = False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'user__phone_number', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TicketMessageInline]
    
    fieldsets = (
        ('اطلاعات تیکت', {
            'fields': ('user', 'subject', 'status')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SiteSetting)