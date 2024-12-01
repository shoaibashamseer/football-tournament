from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class SeatAllocation(models.Model):
    seat_number = models.CharField(max_length=5)
    qr_code_data = models.CharField(max_length=20)

    def __str__(self):
        return self.seat_number


class Attendance(models.Model):
    qr_code_data = models.CharField(max_length=20)
    seat_number = models.CharField(max_length=5)
    date = models.DateField()  
    is_inside = models.BooleanField(default=False) 
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Seat {self.seat_number} ({self.qr_code_data})"

class FirstCheckIn(models.Model):
    date = models.DateField(unique=True)  
    start_time = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"Start Time for {self.date}: {self.start_time}"
