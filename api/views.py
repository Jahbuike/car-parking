from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Tally, ParkingRecord, SystemSetting  # Added SystemSetting here
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm

# --- AUTHENTICATION VIEWS ---

def login_view(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(username=u_name, password=p_word)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('parking_entry')
            else:
                messages.error(request, "Your account is pending Admin approval.")
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'api/login.html')

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  
            user.save()
            messages.info(request, "Registration successful. Please wait for Admin approval.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'api/register.html', {'form': form})

# --- CORE PARKING LOGIC ---

@login_required
def parking_entry_view(request):
    # 1. Handle Form Submission (POST)
    if request.method == "POST":
        name = request.POST.get('name')
        congregation = request.POST.get('congregation')
        plate_number = request.POST.get('plate_number')
        phone_number = request.POST.get('phone_number')
        tally_id = request.POST.get('tally')

        try:
            tally_obj = Tally.objects.get(id=tally_id)
            
            ParkingRecord.objects.create(
                driver_name=name,
                congregation=congregation,
                plate_number=plate_number,
                phone_number=phone_number,
                tally=tally_obj,
                is_checked_out=False 
            )

            tally_obj.is_occupied = True
            tally_obj.save()

            messages.success(request, f"Entry recorded: Tally #{tally_obj.number} assigned to {name}")
            return redirect('parking_entry') 
            
        except Tally.DoesNotExist:
            messages.error(request, "Selected Tally is no longer available.")
            return redirect('parking_entry')

    # 2. Handle Page Load (GET)
    # Fetch settings once
    setting, created = SystemSetting.objects.get_or_create(id=1)
    
    # Fetch active vehicles once
    active_vehicles = ParkingRecord.objects.filter(is_checked_out=False).order_by('-check_in_time')
    
    # Single return statement with all necessary context
    return render(request, 'api/index.html', {
        'active_vehicles': active_vehicles,
        'day_text': setting.current_day_text,
        'setting': setting  
    })
# --- API ENDPOINTS (FOR JAVASCRIPT) ---

@login_required
def get_driver_details(request):
    query = request.GET.get('query', '') 
    
    if len(query) < 3:
        return JsonResponse({'exists': False})

    driver = ParkingRecord.objects.filter(
        Q(driver_name__icontains=query) | 
        Q(plate_number__icontains=query) | 
        Q(phone_number__icontains=query)
    ).order_by('-check_in_time').first()
    
    if driver:
        return JsonResponse({
            'exists': True,
            'record_id': driver.id,
            'name': driver.driver_name, 
            'congregation': driver.congregation,
            'plate_number': driver.plate_number,
            'phone_number': driver.phone_number,
            'is_active': not driver.is_checked_out,
        })
    return JsonResponse({'exists': False})

@login_required
def get_available_tallies(request):
    tallies = list(Tally.objects.filter(is_occupied=False).values('id', 'number'))
    return JsonResponse({'tallies': tallies})

# --- ACTION VIEWS ---

@login_required
def checkout_driver(request, pk):
    record = get_object_or_404(ParkingRecord, pk=pk)
    
    if record.tally:
        tally = record.tally
        tally.is_occupied = False 
        tally.save()
    
    record.is_checked_out = True
    record.save()
    
    messages.success(request, f"Vehicle {record.plate_number} checked out.")
    return redirect('parking_entry')

@login_required
def daily_reset(request):
    if not request.user.is_superuser:
        messages.error(request, "Only the Admin can perform a daily reset.")
        return redirect('parking_entry')

    Tally.objects.all().update(is_occupied=False)
    ParkingRecord.objects.filter(is_checked_out=False).update(is_checked_out=True)
    
    messages.success(request, "System Reset: All tallies are now available.")
    return redirect('parking_entry')