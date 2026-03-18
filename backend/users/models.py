from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Create your models here.

class Role(models.Model):
    """
    Defines what a user can do in the system, 
    Linked back to our planning: Admin, WarehouseManager, 
    StoreManager, Cashier, Auditor
    """

    ADMIN = 'Admin'
    WAREHOUSE_MANAGER = 'WarehouseManager'
    STORE_MANAGER = 'StoreManager'
    CASHIER = 'Cashier'
    AUDITOR = 'Auditor'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'), 
        (WAREHOUSE_MANAGER, 'Warehouse Manager'), 
        (STORE_MANAGER, 'Store Manager'), 
        (CASHIER, 'Cashier'),
        (AUDITOR, 'Auditor'), 
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self): 
        return self.name


