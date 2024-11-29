from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Event, SeatAllocation, Attendance
from datetime import datetime
from django.utils.timezone import now, timedelta
from .models import Attendance, FirstCheckIn, SeatAllocation
from django.utils.timezone import now, timedelta


def event_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'event_id' not in request.session:
            return redirect('login')  # Redirect to login if not logged in
        try:
            request.event = Event.objects.get(id=request.session['event_id'])
        except Event.DoesNotExist:
            return redirect('login')  # Redirect if session is invalid
        return view_func(request, *args, **kwargs)
    return wrapper


def login_page(request):
    if request.method == "POST":
        event_name = request.POST.get('event_name')  
        password = request.POST.get('password')  

        try:
            
            event = Event.objects.get(name=event_name, password=password)
            
            request.session['event_id'] = event.id
            return render(request, 'ticketapp/check_in.html')
 
        except Event.DoesNotExist:
        
            return render(request, 'ticketapp/login.html', {'error': 'Invalid Event Name or Password'})

    return render(request, 'ticketapp/login.html')

@event_login_required
def base_page(request):
    return render(request, 'ticketapp/base.html', {'event': request.event})



@login_required
def check_in_page(request):
    today = datetime.now().date()
    seat_count = Attendance.objects.filter(check_in_time__date=today).count()
    attendees = Attendance.objects.filter(check_in_time__date=today)
    return render(request, 'ticketapp/check_in.html', {'attendees': attendees, 'seat_count': seat_count})


@login_required
def scan_qr(request, action):
    qr_code = request.GET.get('qr_code')
    today = date.today()

    # Fetch seat allocation
    try:
        seat = SeatAllocation.objects.get(qr_code_data=qr_code)
    except SeatAllocation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid QR code'})

    # Check if we have a record of the first check-in for today
    first_check_in, created = FirstCheckIn.objects.get_or_create(date=today)

    if created:
        # This is the first check-in of the day; set start_time
        first_check_in.start_time = now()
        first_check_in.save()

    # Check if 20 hours have passed since the first check-in
    if now() > first_check_in.start_time + timedelta(hours=20):
        # Reset attendance for the day
        Attendance.objects.filter(date=today).update(is_inside=False)
        # Update the first check-in time for the new cycle
        first_check_in.start_time = now()
        first_check_in.save()

    # Proceed with the normal check-in/out logic
    attendance, created = Attendance.objects.get_or_create(
        qr_code_data=qr_code,
        seat_number=seat.seat_number,
        date=today,
        defaults={'is_inside': False}
    )

    if action == 'in':
        if attendance.is_inside:
            return JsonResponse({'status': 'error', 'message': 'Already checked in today'})
        attendance.check_in_time = now()
        attendance.is_inside = True
        attendance.save()
        return JsonResponse({'status': 'success', 'message': f'Seat {attendance.seat_number} marked as arrived'})

    elif action == 'out':
        if not attendance.is_inside:
            return JsonResponse({'status': 'error', 'message': 'Not currently checked in'})
        attendance.check_out_time = now()
        attendance.is_inside = False
        attendance.save()
        return JsonResponse({'status': 'success', 'message': f'Seat {attendance.seat_number} marked as left'})
def scan_page(request):
    return render(request, 'ticketapp/scan.html')

def logout_page(request):
    request.session.flush()  # Clear the session
    return redirect('login')
