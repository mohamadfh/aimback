from django.contrib import admin

# Register your models here.
from .models import Block , Organization , Employee , Manager , Question , UserAnswer
admin.site.register(Block)
admin.site.register(Organization)
admin.site.register(Employee)
admin.site.register(Manager)
admin.site.register(Question)
admin.site.register(UserAnswer)

