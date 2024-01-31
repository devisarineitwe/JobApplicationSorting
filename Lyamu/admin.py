from django.contrib import admin

from Lyamu.models import Employer, Job, Candidate, Application, Selection, Notification, Education

# Register your models here.
admin.site.register(Employer)
admin.site.register(Job)
admin.site.register(Candidate)
admin.site.register(Application)
admin.site.register(Selection)
admin.site.register(Notification)
admin.site.register(Education)