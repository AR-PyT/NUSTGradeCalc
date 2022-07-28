from django.contrib import admin
from .models import GradesB, GradesA, GradesC
# Register your models here.
admin.site.register(GradesB)
admin.site.register(GradesC)
admin.site.register(GradesA)

