from django.shortcuts import render, redirect
from .models import Ride, UserProfile
from django.contrib import messages
from .forms import FeedbackForm
from django.http import JsonResponse
from .models import Feedback
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.core.mail import send_mail
from .forms import EmailForm
from django.contrib.auth.hashers import make_password
import random
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.contrib.auth.decorators import login_required

from django.conf import settings

from django.contrib.gis.measure import D
from datetime import datetime, timedelta


# Create your views here.
def index(request):
     user_name = request.session.get('full_name')  # None if not logged in
     avatar = request.session.get('avatar')
     return render(request, "index.html", {"user_name": user_name, "avatar": avatar})

@login_required
def profile(request):
    # Fetch the user's rides
    rides = Ride.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, "profile.html", {
        "full_name": request.session.get("full_name", request.user.get_full_name()),
        "email": request.session.get("email", request.user.email),
        "phone": request.session.get("phone", ""),
        "aadhaar": request.session.get("aadhaar", ""),
        "gender": request.session.get("gender", ""),
        "avatar": request.session.get("avatar", ""),
        "rides": rides,
    })

@login_required
def cancel_ride(request, ride_id):
    try:
        ride = Ride.objects.get(id=ride_id, user=request.user)
        ride.status = 'canceled'
        ride.save()
    except Ride.DoesNotExist:
        pass
    return redirect('profile')

@login_required
def resume_ride(request, ride_id):
    try:
        ride = Ride.objects.get(id=ride_id, user=request.user)
        ride.status = 'active'
        ride.save()
    except Ride.DoesNotExist:
        pass
    return redirect('profile')

@login_required
def delete_ride(request, ride_id):
    try:
        ride = Ride.objects.get(id=ride_id, user=request.user)
        ride.delete()
    except Ride.DoesNotExist:
        pass  # Optionally log or display an error
    return redirect("profile")



@login_required
def ride_results(request):
    search_params = request.session.get('search_params', {})
    if not search_params:
        return redirect('find_ride')

    user_gender = request.user.gender
    if not user_gender:
        return render(request, 'ride_results.html', {'error': 'Please specify your gender in your profile.'})

    pickup_lat, pickup_lon = map(float, search_params['pickup_coords'].split(','))
    date = search_params['date']
    distance_filter = float(request.GET.get('distance', 2.0))  # Default to 2km

    # Filter active rides by gender and date
    rides = Ride.objects.filter(status='active', date=date)
    if user_gender == 'Male':
        rides = rides.filter(gender__in=['Male', 'any'])
    elif user_gender == 'Female':
        rides = rides.filter(gender__in=['Female', 'any'])
    else:  # 'Other' users see 'any' rides
        rides = rides.filter(gender='any')

    # Calculate distances and filter
    filtered_rides = []
    for ride in rides:
        if not ride.pickup_coords:  # Skip rides without coordinates
            continue
        try:
            ride_lat, ride_lon = map(float, ride.pickup_coords.split(','))
            distance = geodesic((pickup_lat, pickup_lon), (ride_lat, ride_lon)).km
            if distance <= distance_filter:
                cost_per_ride = ride.distance_km * (4 if ride.vehicle_type == 'two-wheeler' else 6)
                filtered_rides.append({
                    'ride': ride,
                    'distance_from_search': round(distance, 2),
                    'cost_per_ride': round(cost_per_ride, 2),
                })
        except (ValueError, AttributeError):
            continue  # Skip rides with invalid coordinates

    return render(request, 'ride_results.html', {
        'rides': filtered_rides,
        'distance_filter': distance_filter,
        'error': None,
    })



def signup(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        aadhaar = request.POST.get("aadhaar")
        gender = request.POST.get("gender")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        avatar = request.FILES.get("avatar") 

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        
        if UserProfile.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered!")
            return redirect("signup")

        
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("signup")

        
        if UserProfile.objects.filter(aadhaar=aadhaar).exists():
            messages.error(request, "Aadhaar number already registered!")
            return redirect("signup")

        # Save user securely
        user = UserProfile(
            full_name=full_name,
            phone=phone,
            email=email,
            aadhaar=aadhaar,
            gender=gender,
            avatar=avatar
        )
        user.set_password(password)  # hashes the password
        user.save()

        messages.success(request, "Signup successful! Please login.")
        return redirect("login")

    return render(request, "signup.html")

def login(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Find user with phone + email
        user = UserProfile.objects.filter(phone=phone, email=email).first()

        if user and user.check_password(password):
            auth_login(request, user)  
            request.session['user_id'] = user.id
            request.session['full_name'] = user.full_name
            request.session['email'] = user.email
            request.session['phone'] = user.phone
            request.session['aadhaar'] = user.aadhaar
            request.session['gender'] = user.gender
            request.session['avatar'] = user.avatar.url if user.avatar else None
            messages.success(request, "Login successful!")
            return redirect("index")  
        else:
            messages.error(request, "Invalid phone, email, or password!")


    return render(request, "login.html")

def logout_view(request):
        logout(request)
        request.session.flush()  # clear custom session values
        return redirect("login")

def aboutus(request):
    return render(request, "aboutus.html")

def forgot_password(request):
    step = "email"  # default step
    success = False

    if request.method == "POST":
        if "femail" in request.POST:  # Step 1: Email check
            femail = request.POST.get("femail")
            if UserProfile.objects.filter(email=femail).exists():
                otp = random.randint(100000, 999999)
                request.session['reset_email'] = femail
                request.session['reset_otp'] = str(otp)

                send_mail(
                    "PASSWORD RESET OTP",
                    f"Your OTP is: {otp}",
                    "your_email@gmail.com",
                    [femail],
                    fail_silently=False,
                )
                success = True
                step = "otp"
            else:
                messages.error(request, "Email not found!")

        elif "otp" in request.POST:  # Step 2: OTP verification
            entered_otp = request.POST.get("otp")
            saved_otp = request.session.get("reset_otp")
            if entered_otp == saved_otp:
                step = "reset"
            else:
                messages.error(request, "Invalid OTP!")

        elif "new_password" in request.POST:  # Step 3: Reset password
            new_password = request.POST.get("new_password")
            femail = request.session.get("reset_email")
            user = UserProfile.objects.get(email=femail)
            user.password = make_password(new_password)  # encrypt password
            user.save()

            messages.success(request, "Password reset successful!")
            return redirect("login")

    return render(request, "forgot_password.html", {"step": step, "success": success})

def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            form = FeedbackForm()  # reset form after save
    else:
        form = FeedbackForm()

    return render(request, 'feedback.html', {'form': form})


def feedback_list(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    data = [
        {
            'name': fb.name,
            'message': fb.message,
            'created_at': fb.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for fb in feedbacks
    ]
    return JsonResponse(data, safe=False)

def feedback_data(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    data = [
        {
            "name": fb.name,
            "message": fb.message,
            "created_at": fb.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for fb in feedbacks
    ]
    return JsonResponse(data, safe=False)

def send_email_view(request):
    success = False
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            send_mail(
                subject,
                message,
                'your_email@gmail.com',   # From email
                [recipient],
                fail_silently=False,
            )
            success = True
    else:
        form = EmailForm()
    
    return render(request, 'send_email.html', {'form': form, 'success': success})

def maptest(request):
    return render(request, "maptest.html")

def distance_view(request):
    distance = None
    error = None
    origin = destination = ""
    origin_lat = origin_lng = dest_lat = dest_lng = None

    if request.method == "POST":
        origin = request.POST.get("origin")
        destination = request.POST.get("destination")

        geolocator = Nominatim(user_agent="myapp")
        loc1 = geolocator.geocode(origin)
        loc2 = geolocator.geocode(destination)

        if loc1 and loc2:
            origin_lat, origin_lng = loc1.latitude, loc1.longitude
            dest_lat, dest_lng = loc2.latitude, loc2.longitude

            distance = round(geodesic((origin_lat, origin_lng), (dest_lat, dest_lng)).km, 2)
        else:
            error = "One or both locations not found."

    return render(request, "distance.html", {
        "origin": origin,
        "destination": destination,
        "distance": distance,
        "origin_lat": origin_lat,
        "origin_lng": origin_lng,
        "destination_lat": dest_lat,
        "destination_lng": dest_lng,
        "error": error
    })

def clean_address(address: str) -> str:
    """
    Clean up long addresses before geocoding.
    Keeps only the first 3 comma-separated parts if it's too detailed.
    """
    if not address:
        return ""
    parts = [p.strip() for p in address.split(",")]
    if len(parts) > 3:
        return ", ".join(parts[:3])  # keep first 3 chunks (more reliable for Nominatim)
    return address


def offer_ride(request):
    if request.method == "POST":
        gender = request.POST.get("gender")
        pickup_address = request.POST.get("pickup_address")
        destination_address = request.POST.get("destination_address")
        pickup_coords = request.POST.get("pickup_coords")
        destination_coords = request.POST.get("destination_coords")
        vehino = request.POST.get("vehino")
        vehiname = request.POST.get("vehiname")
        vehicle_type = request.POST.get("vehicletype")
        date = request.POST.get("date")
        time = request.POST.get("time")

        # Validate coordinates
        try:
            pickup_lat, pickup_lon = map(float, pickup_coords.split(','))
            destination_lat, destination_lon = map(float, destination_coords.split(','))
            pickup = (pickup_lat, pickup_lon)
            destination = (destination_lat, destination_lon)
        except (ValueError, AttributeError):
            return render(request, "success.html", {
                "error": "❌ Invalid location coordinates."
            })

        # Calculate distance and cost
        distance_km = geodesic(pickup, destination).km
        cost = distance_km * 4  # ₹4 per km

        # Save ride to database
        Ride.objects.create(
            user=request.user,
            gender=gender,
            pickup=pickup_address,
            pickup_coords=pickup_coords,  # Save pickup coordinates
            destination=destination_address,
            destination_coords=destination_coords,  # Save destination coordinates
            vehicle_number=vehino,
            vehicle_model=vehiname,
            vehicle_type=vehicle_type,
            date=date,
            time=time,
            distance_km=round(distance_km, 2),
            cost=round(cost, 2)
        )

        return render(request, "success.html", {
            "pickup": pickup_address,
            "destination": destination_address,
            "distance": round(distance_km, 2),
            "cost": round(cost, 2)
        })

    return render(request, "index.html")

@login_required
def find_ride(request):
    if request.method == "POST":
        gender = request.POST.get("gender")
        pickup_address = request.POST.get("from")
        destination_address = request.POST.get("to")
        pickup_coords = request.POST.get("pickup_coords1")
        destination_coords = request.POST.get("destination_coords1")
        date = request.POST.get("date")
        time = request.POST.get("time")
        
        # Validate coordinates
        try:
            pickup_lat, pickup_lon = map(float, pickup_coords.split(','))
            destination_lat, destination_lon = map(float, destination_coords.split(','))
            pickup = (pickup_lat, pickup_lon)
            destination = (destination_lat, destination_lon)
        except (ValueError, AttributeError):
            return render(request, "index.html", {
                "error": "❌ Invalid location coordinates."
            })
        
        # Get all active rides
        all_rides = Ride.objects.filter(status="active")
        
        # Filter by gender preference
        if gender != "any":
            all_rides = all_rides.filter(gender=gender)
        
        # Filter by date (rides on the same day or after)
        if date:
            try:
                search_date = datetime.strptime(date, "%Y-%m-%d").date()
                all_rides = all_rides.filter(date__gte=search_date)
            except ValueError:
                pass
        
        # Calculate distances and filter by route similarity
        matching_rides = []
        for ride in all_rides:
            try:
                # Get ride coordinates if available
                if ride.pickup_coords:
                    ride_pickup_lat, ride_pickup_lon = map(float, ride.pickup_coords.split(','))
                    ride_pickup = (ride_pickup_lat, ride_pickup_lon)
                    
                    # Calculate distance from search pickup to ride pickup
                    pickup_distance = geodesic(pickup, ride_pickup).km
                    
                    # Calculate distance from search destination to ride destination
                    if ride.destination_coords:
                        ride_dest_lat, ride_dest_lon = map(float, ride.destination_coords.split(','))
                        ride_destination = (ride_dest_lat, ride_dest_lon)
                        dest_distance = geodesic(destination, ride_destination).km
                        
                        # Only include rides with reasonable pickup and destination proximity
                        # (within 5km for pickup and 10km for destination)
                        if pickup_distance <= 5 and dest_distance <= 10:
                            ride.pickup_distance = round(pickup_distance, 2)
                            ride.dest_distance = round(dest_distance, 2)
                            matching_rides.append(ride)
            except (ValueError, AttributeError):
                # Skip rides with invalid coordinates
                continue
        
        # Sort by pickup distance
        matching_rides.sort(key=lambda r: r.pickup_distance)
        
        return render(request, "ride_results.html", {
            "rides": matching_rides,
            "search_params": {
                "pickup": pickup_address,
                "destination": destination_address,
                "date": date,
                "time": time,
                "gender": gender
            }
        })
    
    return render(request, "index.html")