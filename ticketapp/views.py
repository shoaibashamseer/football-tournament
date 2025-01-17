from django.shortcuts import render, redirect
from django.http import JsonResponse
from datetime import date
from .models import Event, SeatAllocation, Attendance,FirstCheckIn
from django.utils.timezone import now,timedelta,datetime
from django.core.paginator import Paginator
from django.db import models
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")


        print(f"Debug: Username - {username}, Password - {password}")

        user = authenticate(request,username=username, password=password)
        print(user)
        try:
            if user is not None:
                login(request, user)
                print(f"Debug: Session Key - {request.session.session_key}")
                return redirect('check_in')

            else:
                messages.error(request, "Invalid credentials.")

        except Event.DoesNotExist:

            return render(request, 'ticketapp/login.html', {'error': 'Invalid Event Name or Password'})

    return render(request, 'ticketapp/login.html')


@login_required
def base_page(request):
    return render(request, 'ticketapp/base.html', {'event': request.event})


@login_required
def check_in_page(request):
    today = date.today()


    today_attendees = Attendance.objects.filter(date=today)

    today_checked_in = today_attendees.filter(is_inside=True).count()
    print(today_checked_in)
    today_checked_out = today_attendees.filter(is_inside=False, check_out_time__isnull=False).count()


    previous_day_counts = (
        Attendance.objects.filter(date__lt=today, is_inside=True)
        .values('date')
        .annotate(total_present=models.Count('id'))
        .order_by('date')
    )

    context = {

        'today_checked_in': today_checked_in,
        'today_checked_out': today_checked_out,
        'previous_day_counts': previous_day_counts,
    }

    return render(request, 'ticketapp/check_in.html', context)

def check_in_data(request):
    today = date.today()
    page_number = int(request.GET.get('page', 1))
    attendees = Attendance.objects.filter(date=today)

    paginator = Paginator(attendees, 50)  # 50 records per page
    page_obj = paginator.get_page(page_number)

    attendees_data = [
        {
            'seat_number': attendee.seat_number,
            'is_inside': attendee.is_inside,
            'check_out_time': attendee.check_out_time,
        }
        for attendee in page_obj
    ]

    return JsonResponse({
        'attendees': attendees_data,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
    })

@login_required
def scan_qr(request, action):
    print(f"Action: {action}, QR Code: {request.GET.get('qr_code')}")

    qr_code = request.GET.get('qr_code')
    today = date.today()

    if not qr_code:
        return JsonResponse({'status': 'error', 'message': 'No QR code provided'})


    if action not in ['in', 'out']:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'})

    print(f"Received QR Code: {qr_code}")
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

    #
    attendance, created = Attendance.objects.get_or_create(
        qr_code_data=qr_code,
        seat_number=seat.seat_number,
        date=today,
        defaults={'scanned_by': request.user}
        #defaults={'is_inside': False}
    )

    if action == 'in':
        if attendance.is_inside:
            return JsonResponse({'status': 'error', 'message': 'Already checked in today'})
        attendance.check_in_time = now()
        attendance.is_inside = True
        attendance.save()
        return JsonResponse({'status': 'success', 'message': f'Seat {attendance.seat_number} marked as arrived', 'redirect_url': '/check-in/'})

    elif action == 'out':
        if not attendance.is_inside:
            return JsonResponse({'status': 'error', 'message': 'Not currently checked in'})
        attendance.check_out_time = now()
        attendance.is_inside = False
        attendance.save()
        return JsonResponse({'status': 'success', 'message': f'Seat {attendance.seat_number} marked as left', 'redirect_url': '/check-in/'})


@login_required
def detailed_view(request):

    selected_date = request.GET.get('date')
    if selected_date:
        try:

            try:
                date_to_show = datetime.strptime(selected_date, "%Y-%m-%d").date()
            except ValueError:
                date_to_show = datetime.strptime(selected_date, "%b. %d, %Y").date()
        except ValueError:
            return render(request, 'ticketapp/details.html', {'error': 'Invalid date format'})
    else:

        date_to_show = now().date()


    attendees = Attendance.objects.filter(date=date_to_show).order_by('check_in_time')

    # Paginate the attendees
    paginator = Paginator(attendees, 50)  # Show 50 records per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Pass the selected date to the template
    return render(request, 'ticketapp/details.html', {
        'selected_date': date_to_show,
        'today_page': page_obj,
    })


def scan_page(request):
    return render(request, 'ticketapp/scan.html')

def logout_page(request):
    request.session.flush()  # Clear the session
    return redirect('login')
