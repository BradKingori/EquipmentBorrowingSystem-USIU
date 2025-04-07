from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.contrib.contenttypes.models import ContentType


class CustomUser(AbstractUser):  # Ensure this is inside `equipment/models.py`
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('hod', 'Head of Department'),
        ('technician', 'Technician'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    fullname = models.CharField(max_length=300, null=True, blank=True)
    email = models.EmailField(unique = True, null=True, blank=True)
    password = models.CharField(max_length=500, null=True, blank=True)
    userId = models.IntegerField(unique = True, null=True, blank=True) 
    username = models.CharField(unique= True, max_length= 300, null=True, blank=True)
    #username = None  # Remove the username field completely
    #USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname', 'role', 'userId', 'email']

    def __str__(self):
        return f"{self.fullname} ({self.role})"

class Equipment(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('damaged', 'Damaged'),
    ]
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=50, unique=True)
    available = models.BooleanField(default=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')

    class Meta:
        permissions = [
            ("modify_equipment", "Can modify equipment"),
        ]

    def __str__(self):
        return f"({self.name}{self.brand}) - {self.condition}"


class BorrowRequest(models.Model):
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("denied", "Denied"),
    ] """

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    #status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    lecturer_approved = models.BooleanField(default=  False)
    hod_approved = models.BooleanField(default= False)
    tech_approved =  models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("approve_borrowrequest", "Can approve borrow requests"),
        ]

    def fully_approved(self):
        return self.lecturer_approved and self.hod_approved and self.tech_approved
    
    def save(self, *args, **kwargs):
        if self.student and self.student.role != "student":
            raise ValueError("Only students can make borrow requests.")
        super().save(*args, **kwargs)
