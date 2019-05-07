from django.contrib import admin
from .models import TagingList, TagingData

# Register your models here.
admin.site.register(TagingList)
admin.site.register(TagingData)