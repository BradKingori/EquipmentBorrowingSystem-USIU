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
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import BorrowRequest, Equipment
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # To display messages
from .models import Equipment
from .forms import EquipmentForm

def dashboard(request):
    return render(request, 'equipment/dashboard.html')


def index(request):
    return render(request, 'equipment/base.html')

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
    if not request.user.is_authenticated:  # Check if the user is logged in
        return redirect('login')  # Redirect to login if anonymous
    
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
    context = {'requests': requests}
    return render(request, 'equipment/lecturer_dashboard.html', context)

@login_required
@allowed_users(allowed_roles=['hod'])
def hod_dashboard(request):
    requests = BorrowRequest.objects.filter(hod_approved=False)
    context = {'requests': requests}
    return render(request, 'equipment/hod_dashboard.html', context)

@login_required
@allowed_users(allowed_roles=['technician'])
def technician_dashboard(request):
    requests = BorrowRequest.objects.filter(tech_approved=False)
   
    if request.method == "POST":
        equipment_serial = request.POST.get("serial_number")  # Get ID for editing, if available
        if equipment_serial:
            equipment = Equipment.objects.get(serial_number=equipment_serial)  # Retrieve existing equipment
        else:
            equipment = Equipment()  # Create new

        # Assign form data
        equipment.name = request.POST.get('name', '')
        equipment.brand = request.POST.get('brand', '')
        equipment.serial_number = request.POST.get('serial_number', '')
        equipment.available = request.POST.get('available') == 'on'
        equipment.save()
        return redirect('technician_dashboard')
        
    context = {"requests": requests}
    return render(request, "equipment/technician_dashboard.html", context)

@login_required
@allowed_users(allowed_roles=['student'])
def student_dashboard(request):
    equipments = Equipment.objects.filter(available = True)
    if request.method == "POST":
        equipment_id = request.POST.get("equipment_id")
        equipment = Equipment.objects.get(id=equipment_id)
        #equipment = get_object_or_404(Equipment, id=equipment_id)
        #student = CustomUser.objects.get(id=request.user.id)
        student = request.user
        BorrowRequest.objects.create(student = student, equipment=equipment)


        """
        if equipment.available:
            if not BorrowRequest.objects.filter(student=student, equipment=equipment).exists():
                BorrowRequest.objects.create(student=student, equipment=equipment)
        
        
        from datetime import timedelta
        from datetime import timedelta
        from django.utils.timezone import now

        time_limit = now() - timedelta(days=7)  # Example: 7-day restriction

        existing_request = BorrowRequest.objects.filter(
            student=student, 
            equipment=equipment,
            created_at__gte=time_limit  # Ensures request is older than 7 days
        ).exclude(status="denied").exists()

        """
    context = {"equipments": equipments}
    return render(request, "equipment/student_dashboard.html", context)

@permission_required('equipment.approve_borrowrequest', raise_exception=True)
def approve_request(request, request_id):
    if request.method == "POST":
        #req_id = request.POST.get("request_id")
        borrow_request = BorrowRequest.objects.get(id=request_id)

        #borrow_request = get_object_or_404(BorrowRequest, id=req_id)

        if request.user.groups.filter(name="lecturer").exists():
            borrow_request.lecturer_approved = True
        elif request.user.groups.filter(name="hod").exists():
            borrow_request.hod_approved = True
        elif request.user.groups.filter(name="technician").exists():
            borrow_request.tech_approved = True

        borrow_request.save()
    return redirect(request.user.groups.first().name + '_dashboard')


def borrowRequests(request):
    borrow_requests = BorrowRequest.objects.all()

    if request.user.role == "student":
        student=request.user
        borrow_requests = BorrowRequest.objects.filter(student=student)

    context = {'borrow_requests': borrow_requests}
    return render(request, 'equipment/borrow_requests.html', context)


def equipments(request):
    equipments = Equipment.objects.all()
    context = {'equipments': equipments}
    return render(request, 'equipment/equipment.html', context)


def signout(request):
      logout(request)
      messages.success(request, 'Logout successfully')
      return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user= CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None


@login_required
@allowed_users(allowed_roles=['hod'])
def hod_dashboard(request):
    requests = BorrowRequest.objects.filter(hod_approved=False)
    context = {'requests': requests}
    return render(request, 'equipment/hod_dashboard.html', context)

@login_required
@allowed_users(allowed_roles=['hod'])
def reject_request(request, request_id):
    # Retrieve the borrow request object
    borrow_request = BorrowRequest.objects.get(id=request_id)
    
    # Set the status of the borrow request to rejected (if necessary)
    borrow_request.hod_approved = False  # Or you can have a field `rejected=True` if you prefer
    borrow_request.save()

    # Set the associated equipment to unavailable
    equipment = borrow_request.equipment
    equipment.available = False
    equipment.save()

    # Optionally, you can display a success message
    messages.success(request, f'Request for {equipment.name} rejected and marked as unavailable.')

    # Redirect back to the HOD dashboard
    return redirect('hod_dashboard')





def add_equipment(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipment added successfully.")
            return redirect('technician_dashboard')  # Redirect to technician dashboard or another page
        else:
            messages.error(request, "There was an error adding the equipment.")
    else:
        form = EquipmentForm()
    return render(request, 'equipment/add_equipment.html', {'form': form})

def modify_equipment(request, equipment_id):
    # Use get_object_or_404 to catch missing equipment gracefully
    equipment = get_object_or_404(Equipment, id=equipment_id)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipment updated successfully.")
            return redirect('technician_dashboard')  # Redirect to technician dashboard or another page
        else:
            messages.error(request, "There was an error updating the equipment.")
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'equipment/modify_equipment.html', {'form': form, 'equipment': equipment})
