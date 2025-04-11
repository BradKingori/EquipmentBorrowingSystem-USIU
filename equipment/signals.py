from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def assign_group(sender, instance, created, **kwargs):
    if created:  
        group_name = instance.role  # Assuming `role` matches group names

        # Assign user to the corresponding group
        group, created = Group.objects.get_or_create(name=group_name)
        instance.groups.add(group)

        # Assign permissions to groups (only on first group creation)
        if created:
            if group_name == "technician":
                permission = Permission.objects.get(codename="modify_equipment")
                group.permissions.add(permission)

            elif group_name in ["hod", "lecturer"]:
                permission = Permission.objects.get(codename="approve_borrowrequest")
                group.permissions.add(permission)