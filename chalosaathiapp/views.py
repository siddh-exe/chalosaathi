from django.shortcuts import render, redirect
from .models import UserProfile
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


# Create your views here.
def index(request):
     user_name = request.session.get('full_name')  # None if not logged in
     avatar = request.session.get('avatar')
     return render(request, "index.html", {"user_name": user_name, "avatar": avatar})

def profile(request):
    return render(request, "profile.html", {
        "full_name": request.session.get("full_name"),
        "email": request.session.get("email"),
        "phone": request.session.get("phone"),
        "aadhaar": request.session.get("aadhaar"),
        "gender": request.session.get("gender"),
        "avatar": request.session.get("avatar"),
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
