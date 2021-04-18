from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

# Reference: https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model
class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **other_fields):
        """
        Create and save a user.
        All fields required.
        """
        if not username or not email:
            raise ValueError(_('The email and username must be set.'))
        email = self.normalize_email(email)

        user = self.model(username=username, email=email, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(_('superuser should have staff permission.'))
        if other_fields.get('is_superuser') is not True:
            raise ValueError(_('superuser should have superuser permission.'))
        if other_fields.get('is_active') is not True:
            raise ValueError(_('superuser should have active permission.'))
        return self.create_user(username, email, password, **other_fields)

class Truck(models.Model):
    truck_id=models.AutoField(primary_key=True)
    x=models.IntegerField(default=1)
    y=models.IntegerField(default=1)
    status=models.TextField(default='idle')

class User(AbstractBaseUser):
    """
    A customized user model designed for this project.
    Every User should have three fields: username, email, password.
    """
    username = models.CharField(max_length=40, unique=True, blank=False)
    email = models.EmailField(_('email address'), blank=False, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # The user can access its shared rides by
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username


class Package(models.Model):
    PACKAGE_STATUS = [
    ("packing", "packing"),
    ("packed", "packed"),
    ("loading", "loading"),
    ("loaded", "loaded"),
    ("delivering", "delivering"),
    ("delivered", "delivered")
    ]
    package_id = models.IntegerField()
    tracking_num = models.CharField(max_length = 30, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name = "package_set")
    package_status = models.CharField(max_length = 30, choices = PACKAGE_STATUS, default = 'packing')
    dest_x = models.IntegerField(null=True)
    dest_y = models.IntegerField(null=True)
    wh_id = models.IntegerField(null=True)
    wh_x = models.IntegerField(null=True)
    wh_y = models.IntegerField(null=True)
    #truck_id = models.IntegerField(null=True)
    truck=models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True)
    #product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return f'{self.package_id}'


class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_description = models.TextField()
    product_count = models.IntegerField(null=True)
    product_package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)