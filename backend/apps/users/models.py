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

class UserManager(BaseUserManager):
    """Custom manager - tells Djnago how to create users for our model."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) #hash password
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using email instead of username.
    Linked to our data model: User entity from module 7. 
    """

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    role = models.ForeignKey(
        Role, 
        on_delete=models.PROTECT, #Can't delete a role that has users
        null=True, 
        blank=True, 
        related_name='users'
    )
    location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='staff'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta: 
        db_table = 'users'
        verbose_name = 'User'
    
    def __str__(self): 
        return f"{self.name} ({self.email})"
