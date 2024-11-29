from django.contrib import admin
from .models import Event, SeatAllocation, Attendance, FirstCheckIn

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name',)
    ordering = ('start_date',)


@admin.register(SeatAllocation)
class SeatAllocationAdmin(admin.ModelAdmin):
    list_display = ('seat_number', 'qr_code_data')
    search_fields = ('seat_number', 'qr_code_data')
    ordering = ('seat_number',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('seat_number', 'qr_code_data', 'date', 'is_inside', 'check_in_time', 'check_out_time')
    list_filter = ('date', 'is_inside')
    search_fields = ('seat_number', 'qr_code_data')
    ordering = ('-date', 'seat_number')
    actions = ['reset_attendance']

    def reset_attendance(self, request, queryset):
        queryset.update(is_inside=False, check_in_time=None, check_out_time=None)
        self.message_user(request, "Selected attendance records have been reset.")
    reset_attendance.short_description = "Reset selected attendance"

@admin.register(FirstCheckIn)
class FirstCheckInAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time')
    ordering = ('-date',)

