from django.contrib import admin
from questionFilter.models import *
# Register your models here.
admin.site.register(Question)
admin.site.register(Company)
admin.site.register(CompanyTag)
admin.site.register(Algorithm)
admin.site.register(AlgorithmTag)
admin.site.register(Similar)
