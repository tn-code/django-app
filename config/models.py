from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None):
        if not username:
            raise ValueError('Users must have a username')
        elif not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.username = self.username,
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, username, email, password):
        user = self.create_user(
            username,
            email,
            password=password,
        )
        user.username = self.username,
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(
            username,
            email,
            password=password,
        )
        user.username = self.username,
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    # notice the absence of a "Password field", that's built in.

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __str__(self):              # __unicode__ on Python 2
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

    objects = UserManager()
