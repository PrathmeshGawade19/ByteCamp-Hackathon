from django import forms
from .models import Complaint
from django import forms
from .models import ComplaintComment

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'description', 'image', 'location_name', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class ComplaintCommentForm(forms.ModelForm):
    class Meta:
        model = ComplaintComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows':2, 'placeholder':'Add a comment...'})
        }