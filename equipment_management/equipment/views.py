from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .decorators import unauthenticated_user, allowed_users
from .models import BorrowRequest, Equipment, CustomUser
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import generate_token
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from equipment_management import settings
from django.shortcuts import get_object_or_404, redirect


def dashboard(request):
    return render(request, 'equipment/dashboard.html')

def index(request):
    return render(request, 'equipment/base.html')


def signup(request):
    if request.method == "POST":
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
            messages.error(request, "This user ID is already in use")
            return redirect('signup')

        if password != pass2:
            messages.error(request, "Passwords did not match!")
            return redirect('signup')

        username = email.split('@')[0]
        original_username = username
        count = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{original_username}{count}"
            count += 1

        CustomUser.objects.create_user(
            username=username, fullname=fullname, email=email,
            password=password, role=role, userId=userId
        )

        return redirect('login')

    return render(request, "equipment/signup.html")


@unauthenticated_user
def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        try:
            user_obj = CustomUser.objects.get(email=email)
            username = user_obj.username
        except CustomUser.DoesNotExist:
            messages.error(request, "Wrong credentials")
            return render(request, "equipment/login.html", {"email": email})

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('redirect_dashboard')
        else:
            messages.error(request, "Wrong credentials")
            return render(request, "equipment/login.html", {"email": email})

    return render(request, "equipment/login.html")


def redirect_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    role_redirects = {
        'student': 'student_dashboard',
        'lecturer': 'lecturer_dashboard',
        'hod': 'hod_dashboard',
        'technician': 'technician_dashboard',
    }

    return redirect(role_redirects.get(request.user.role, 'login'))


@login_required(login_url='redirect_dashboard')
@allowed_users(allowed_roles=['lecturer'])
def lecturer_dashboard(request):
    requests = BorrowRequest.objects.filter(lecturer_approved=False)
    return render(request, 'equipment/lecturer_dashboard.html', {'requests': requests})


@login_required
@allowed_users(allowed_roles=['hod'])
def hod_dashboard(request):
    requests = BorrowRequest.objects.filter(hod_approved=False)
    return render(request, 'equipment/hod_dashboard.html', {'requests': requests})

@login_required
@allowed_users(allowed_roles=['technician'])
def technician_dashboard(request):
    requests = BorrowRequest.objects.filter(tech_approved=False)
    equipments = Equipment.objects.all()  # Get all equipment to display and delete

    if request.method == "POST" and 'name' in request.POST:
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        serial_number = request.POST.get('serial_number')
        available = request.POST.get('available') == 'on'

        if not Equipment.objects.filter(serial_number=serial_number).exists():
            Equipment.objects.create(
                name=name,
                brand=brand,
                serial_number=serial_number,
                available=available
            )
        else:
            messages.warning(request, f"Equipment with serial {serial_number} already exists.")

        return redirect('technician_dashboard')

    return render(request, "equipment/technician_dashboard.html", {
        "requests": requests,
        "equipments": equipments
    })



@login_required
@allowed_users(allowed_roles=['technician'])
def technician_dashboard(request):
    requests = BorrowRequest.objects.filter(tech_approved=False)

    if request.method == "POST":
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        serial_number = request.POST.get('serial_number')
        available = request.POST.get('available') == 'on'

        if not Equipment.objects.filter(serial_number=serial_number).exists():
            Equipment.objects.create(
                name=name,
                brand=brand,
                serial_number=serial_number,
                available=available
            )
        else:
            messages.warning(request, f"Equipment with serial {serial_number} already exists.")

        return redirect('technician_dashboard')

    return render(request, "equipment/technician_dashboard.html", {"requests": requests})


@login_required
@allowed_users(allowed_roles=['student'])
def student_dashboard(request):
    equipments = Equipment.objects.filter(available=True)

    if request.method == "POST":
        equipment_id = request.POST.get("equipment_id")
        equipment = Equipment.objects.get(id=equipment_id)
        student = request.user
        BorrowRequest.objects.create(student=student, equipment=equipment)

    return render(request, "equipment/student_dashboard.html", {"equipments": equipments})


@permission_required('equipment.approve_borrowrequest', raise_exception=True)
def approve_request(request, request_id):
    if request.method == "POST":
        borrow_request = BorrowRequest.objects.get(id=request_id)

        if request.user.groups.filter(name="lecturer").exists():
            borrow_request.lecturer_approved = True
        elif request.user.groups.filter(name="hod").exists():
            borrow_request.hod_approved = True
        elif request.user.groups.filter(name="technician").exists():
            borrow_request.tech_approved = True

        borrow_request.save()

    return redirect(f"{request.user.groups.first().name}_dashboard")


def borrowRequests(request):
    borrow_requests = BorrowRequest.objects.all()

    if request.user.role == "student":
        borrow_requests = BorrowRequest.objects.filter(student=request.user)

    return render(request, 'equipment/borrow_requests.html', {'borrow_requests': borrow_requests})


def equipments(request):
    equipments = Equipment.objects.all()
    return render(request, 'equipment/equipment.html', {'equipments': equipments})


def signout(request):
    logout(request)
    messages.success(request, 'Logout successfully')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
