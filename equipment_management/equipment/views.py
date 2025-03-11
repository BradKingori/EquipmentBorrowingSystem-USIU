from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import BorrowRequest, Equipment
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .tokens import generate_token
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from equipment_management import settings
from django.utils.encoding import force_bytes, force_text



"""
from django.contrib.auth.hashers import make_password, check_password

hashed_pwd = make_password("plain_text")
check_password("plain_text",hashed_pwd)  # returns True
"
"""



def signup(request):
    if request.method =="POST":
        fullname = request.POST['fullname'] 
        email = request.POST['email']       
        password = request.POST['password']
        pass2 = request.POST['pass2']
        userId = request.POST['userId']
        role = request.POST['role']  
        
        if CustomUser.objects.filter(email=email):
                messages.error(request, "Email already exists! Please try again")
                return redirect('register')
        
        if CustomUser.objects.filter(userId=userId):
                messages.error(request,"This user ID is already in use")
                return redirect('register')
        
        if password != pass2:
                messages.error(request, "Passwords did not match!")     

        # Extract username from email (everything before @)
        username = email.split('@')[0]  

        # Ensure the generated username is unique
        original_username = username
        count = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{original_username}{count}"  # Append a number to avoid duplicates
            count += 1
   
        CustomUser.objects.create_user(username=username, fullname= fullname, email=email, password=password, role=role, userId=userId)                                
        #user.is_active = False
        #user.save()

        #messages.success(request, "Your account has been created successfully. Please check your email for email verification.")
        """
        #Verification email
        current_site = get_current_site(request)    
        verification_message = render_to_string('equipment/email_verification.html',{
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':generate_token.make_token(user),
        })
        subject="Verify your email"
        from_email=settings.EMAIL_HOST_USER
        to_list=[user.email]
        message = EmailMessage(subject, verification_message, from_email, to_list)            
        message.content_subtype="html"
        message.fail_silently = False
        message.send()

        """

        return redirect('login')

    return render(request, "equipment/signup.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        """
        email = request.POST.get('email', '').strip()  
        password = request.POST.get('password', '').strip()

        """

         # Fetch the actual username associated with the email
        try:
            user_obj = CustomUser.objects.get(email=email)
            username = user_obj.username  # Use the correct username from the database
        except CustomUser.DoesNotExist:
            messages.error(request, "Wrong credentials")
            return render(request, "equipment/login.html", {"email": email})

        user = authenticate(username = username, password=password)

        if  user is not None:
                login(request, user)
                return redirect('redirect_dashboard')  # Adjust the redirect destination as needed
        else:
                messages.error(request, "Wrong credentials")
                return render(request, "equipment/login.html", {"email": email})  # Stay on login page

        
    return render(request, "equipment/login.html")


@login_required
def redirect_dashboard(request):
    if request.user.role == 'student':
        return redirect('student_dashboard')
    elif request.user.role == 'lecturer':
        return redirect('lecturer_dashboard')
    elif request.user.role == 'hod':
        return redirect('hod_dashboard')
    elif request.user.role == 'technician':
        return redirect('technician_dashboard')
    return redirect('login')


@login_required
def student_dashboard(request):
    equipment_list = Equipment.objects.filter(available= True)
    if request.method == "POST":
        equipment_id = request.POST.get("equipment_id")
        equipment = request.objects.get(id=equipment_id)
        student = CustomUser.objects.get(user= request.user)
        BorrowRequest.objects.create(student = student,equipment=equipment)
        return redirect("student_dashboard")
    
    return render(request, "equipment/student_dashboard.html", {"equipment_list": equipment_list} )


@login_required
def lecturer_dashboard(request):
    requests = BorrowRequest.objects.filter(lecturer_approved = False)
    if (request.method == "POST"):
        req_id = request.POST.get("request_id")
        request_obg = BorrowRequest.objects.get(id=req_id)
        request_obg.lecturer_approved = True
        request_obg.save()
        return redirect("lecturer_dashboard")
    
    return render (request, 'equipment/lecturer_dashboard.html', {'requests':requests})


@login_required
def hod_dashboard(request):
    requests = BorrowRequest.objects.filter(lecturer_approved = True , hod_approved = False)
    if (request.method == "POST"):
        req_id = requests.POST.get("request_id")
        request_obj = BorrowRequest.objects.get(id=req_id)
        request_obj.hod_approved = True
        request_obj.save()
        return redirect("hod_dashboard")
    
    return render(request , "equipment/hod_dashboard.html", {'requests':requests})

@login_required
def technician_dashboard(request):
    requests = BorrowRequest.objects.filter(lecturer_approved =  True,hod_approved = True )
    if(request.method == "POST"):
        req_id = requests.POST.get("request_id")
        request_obj = BorrowRequest.objects.get(id=req_id)
        request_obj.tech_approved = True
        request_obj.save()
        return redirect(technician_dashboard)
    
    return render(request, "equipment/technician_dashboard.html",{"requests": request})

def signout(request):
      logout(request)
      messages.success(request, 'Logout successfully')
      return redirect('signup')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user= CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('redirect_dashboard')
    else:
        return render(request, 'equipment/activation_failed.html')


