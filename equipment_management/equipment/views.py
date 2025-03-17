from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, permission_required

from .decorators import unauthenticated_user, allowed_users
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
from django.contrib.auth.decorators import user_passes_test

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
                return redirect('signup')
        
        if CustomUser.objects.filter(userId=userId):
                messages.error(request,"This user ID is already in use")
                return redirect('signup')
        
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

@unauthenticated_user
def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

         # Fetch the actual username associated with the email
        try:
            user_obj = CustomUser.objects.get(email=email)
            username = user_obj.username  # Use the correct username from the database
        except CustomUser.DoesNotExist:
            messages.error(request, "Wrong credentials")
            return render(request, "equipment/login.html", {"email": email})

        user = authenticate(username = username, password=password)

        if user is not None:
                login(request, user)
                return redirect('redirect_dashboard')  # Adjust the redirect destination as needed
        else:
                messages.error(request, "Wrong credentials")
                return render(request, "equipment/login.html", {"email": email})  # Stay on login page

    return render(request, "equipment/login.html")


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


@login_required(login_url='redirect_dashboard')
@allowed_users(allowed_roles=['lecturer'])
def lecturer_dashboard(request):
    requests = BorrowRequest.objects.filter(lecturer_approved=False)
    return render(request, 'equipment/lecturer_dashboard.html', {'requests': requests})

@login_required
@allowed_users(allowed_roles=['hod'])
def hod_dashboard(request):
    requests = BorrowRequest.objects.filter(lecturer_approved=True, hod_approved=False)
    return render(request, 'equipment/hod_dashboard.html', {'requests': requests})

@login_required
@allowed_users(allowed_roles=['technician'])
def technician_dashboard(request):
    equipments = Equipment.objects.all()
    requests = BorrowRequest.objects.filter(lecturer_approved=True, hod_approved=True, tech_approved=True)
    return render(request, "equipment/technician_dashboard.html", {"equipment": equipments, "requests": requests})

"""


@login_required
@permission_required('equipment.modify_equipment', raise_exception=True)
def technician_dashboard(request):
    if request.user.role != 'technician':
        messages.error(request, "You do not have access to this page.")
        return redirect('redirect_dashboard')


    requests = BorrowRequest.objects.filter(lecturer_approved=True, hod_approved=True, tech_approved=False)
    #Full page that has a list of equipments and borrow requests, with approved and not approved requests
    # 
    equipments = Equipment.objects.all() #get all equipments 
    
    #Perhaps a button where a technician can change the status of an equipment from available to not available, add or delete equipment
    
    equipment_id = request.POST.get("equipment_id")
    equipment = Equipment.objects.get(id=equipment_id)
        
    if request.method == "POST":
        equipment.name = request.POST['name']
        equipment.brand = request.POST['brand']
        equipment.available = request.POST['available'] == 'on'
        equipment.save()
        return redirect('technician_dashboard')
    return render(request, "equipment/technician_dashboard.html", {"requests": requests, "equipment": equipments})


"""

@login_required
@allowed_users(allowed_roles=['student'])
def student_dashboard(request):
    equipment_list = Equipment.objects.filter(available= True)
    if request.method == "POST":
        equipment_id = request.POST.get("equipment_id")
        equipment = Equipment.objects.get(id=equipment_id)
        student = CustomUser.objects.get(id=request.user.id)
        BorrowRequest.objects.create(student = student,equipment=equipment)
        return redirect("student_dashboard")
    
    #STUDENT CAN CREATE BORROW REQUEST, MAYBE PICK SPECIFIC LECTURER TO APPROVE 
    return render(request, "equipment/student_dashboard.html", {"equipment_list": equipment_list})

@permission_required('equipment.approve_borrowrequest', raise_exception=True)
def approve_request(request, request_id):
    borrow_request = BorrowRequest.objects.get(id=request_id)

    if request.user.groups.filter(name="lecturer").exists():
        borrow_request.lecturer_approved = True
    elif request.user.groups.filter(name="hod").exists():
        borrow_request.hod_approved = True
    elif request.user.groups.filter(name="technician").exists():
        borrow_request.tech_approved = True

    borrow_request.save()
    return redirect(request.user.groups.first().name + '_dashboard')

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
