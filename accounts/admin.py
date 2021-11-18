from django.contrib import admin

# Register your models here.
from accounts.models import MyUser,Profile,CareSeeker,CareTaker,Friend_Request,Comments



admin.site.register(MyUser),
admin.site.register(Profile),
admin.site.register(CareSeeker),
admin.site.register(CareTaker),
admin.site.register(Friend_Request),
admin.site.register(Comments)