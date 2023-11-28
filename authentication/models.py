from django.contrib import admin
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    role = models.CharField(choices=[('A', 'Admin'),
                                     ('M', 'Manager'),
                                     ('E', 'Employee')
                                     ],
                            max_length=1)

    @property
    def fullname(self):
        return self.first_name + ' ' + self.last_name + " ," + self.username

    def is_completed(self):
        return self.first_name != '' and self.first_name is not None \
            and self.last_name != '' and self.last_name is not None
