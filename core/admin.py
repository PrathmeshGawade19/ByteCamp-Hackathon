from django.contrib import admin
from .models import Category, Complaint, ComplaintUpvote, ComplaintComment

admin.site.register(Category)
admin.site.register(Complaint)
admin.site.register(ComplaintUpvote)
admin.site.register(ComplaintComment)
