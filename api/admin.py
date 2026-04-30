from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.html import format_html
from .models import Tally, ParkingRecord, SystemSetting

# --- 1. ADMIN BRANDING ---
admin.site.site_header = "CargoConnect Parking System"
admin.site.site_title = "CargoConnect Admin"
admin.site.index_title = "Welcome to Parking Management"

# --- 2. FORMS ---
class TallyGenerationForm(forms.Form):
    count = forms.IntegerField(
        min_value=1, 
        max_value=500, 
        label="How many tallies to create?",
        help_text="Starts from the last available tally number."
    )

# --- 3. USER ADMIN (Approval Logic) ---
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff')
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_active=True)
    approve_users.short_description = "Approve selected users"

# --- 4. TALLY ADMIN (Merged Badge + Bulk Action) ---
@admin.register(Tally)
class TallyAdmin(admin.ModelAdmin):
    list_display = ('number', 'status_badge', 'is_occupied')
    list_editable = ('is_occupied',)
    list_filter = ('is_occupied',)
    ordering = ('number',)
    actions = ['generate_multiple_tallies']

    # --- Visual Badge Logic ---
    def status_badge(self, obj):
        if obj.is_occupied:
            return format_html(
                '<span style="background: #fee2e2; color: #b91c1c; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.7rem;">{}</span>',
                "OCCUPIED"
            )
        return format_html(
            '<span style="background: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.7rem;">{}</span>',
            "AVAILABLE"
        )
    status_badge.short_description = 'Visual Status'

    # --- Bulk Action Logic ---
    def generate_multiple_tallies(self, request, queryset):
        if 'apply' in request.POST:
            form = TallyGenerationForm(request.POST)
            if form.is_valid():
                count = form.cleaned_data['count']
                last_tally = Tally.objects.all().order_by("-number").first()
                start_num = (last_tally.number + 1) if last_tally else 1
                
                new_tallies = [
                    Tally(number=i, is_occupied=False) 
                    for i in range(start_num, start_num + count)
                ]
                Tally.objects.bulk_create(new_tallies)
                
                self.message_user(request, f"Successfully created {count} new tallies.", messages.SUCCESS)
                return HttpResponseRedirect(request.get_full_path())

        form = TallyGenerationForm()
        return render(request, 'admin/tally_generate_form.html', {
            'items': queryset,
            'form': form,
            'title': 'Bulk Generate Tallies'
        })
    generate_multiple_tallies.short_description = "🚀 Bulk Generate New Tallies"

# --- 5. PARKING RECORD ADMIN ---
@admin.register(ParkingRecord)
class ParkingAdmin(admin.ModelAdmin):
    list_display = ('driver_name', 'plate_number', 'tally', 'is_checked_out', 'check_in_time')
    search_fields = ('driver_name', 'plate_number', 'phone_number')
    list_filter = ('is_checked_out', 'congregation', 'check_in_time')
    list_editable = ('is_checked_out',)

# --- 6. SYSTEM SETTINGS ADMIN ---
@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('current_day_text', 'banner_bg_color', 'tally_active_color')
    
    fieldsets = (
        ('General Content', {
            'fields': ('current_day_text',)
        }),
        ('Banner Styling', {
            'fields': ('banner_bg_color', 'banner_text_color'),
        }),
        ('Tally Button Styling', {
            'fields': ('tally_bg_color', 'tally_active_color'),
        }),
    )

    def has_add_permission(self, request):
        return not SystemSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False