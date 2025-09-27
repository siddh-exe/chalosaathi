from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Feedback'}),
        }

class EmailForm(forms.Form):
    recipient = forms.EmailField(label="Recipient Email")
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)