from django import forms
from .models import Feedback
from .models import Ride

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



class FindRideForm(forms.Form):
    pickup = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'from', 'placeholder': 'Enter Pickup Location'}),
        required=True
    )
    pickup_coords = forms.CharField(widget=forms.HiddenInput(), required=True)
    destination = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'to', 'placeholder': 'Enter Destination'}),
        required=True
    )
    destination_coords = forms.CharField(widget=forms.HiddenInput(), required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'id': 'date', 'type': 'date'}), required=True)
    time = forms.TimeField(widget=forms.TimeInput(attrs={'id': 'time', 'type': 'time'}), required=True)

    def clean(self):
        cleaned_data = super().clean()
        pickup_coords = cleaned_data.get('pickup_coords')
        destination_coords = cleaned_data.get('destination_coords')
        try:
            float(pickup_coords.split(',')[0]), float(pickup_coords.split(',')[1])
            float(destination_coords.split(',')[0]), float(destination_coords.split(',')[1])
        except (ValueError, IndexError, AttributeError):
            raise forms.ValidationError("Please select valid pickup and destination locations from the suggestions.")
        return cleaned_data

class RideForm(forms.ModelForm):
    pickup_coords = forms.CharField(widget=forms.HiddenInput(), required=True)
    destination_coords = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Ride
        fields = ['gender', 'pickup', 'pickup_coords', 'destination', 'destination_coords', 'vehicle_number', 'vehicle_model', 'vehicle_type', 'date', 'time']
        widgets = {
            'gender': forms.Select(attrs={'id': 'gender2'}),
            'pickup': forms.TextInput(attrs={'id': 'from2', 'placeholder': 'Enter Pickup Location'}),
            'destination': forms.TextInput(attrs={'id': 'to2', 'placeholder': 'Enter Destination'}),
            'vehicle_number': forms.TextInput(attrs={'id': 'vehino', 'placeholder': 'Enter Vehicle Registration Number'}),
            'vehicle_model': forms.TextInput(attrs={'id': 'vehiname', 'placeholder': 'Enter Vehicle Model Name'}),
            'vehicle_type': forms.Select(attrs={'id': 'vehicletype'}),
            'date': forms.DateInput(attrs={'id': 'date2', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'id': 'time2', 'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pickup_coords = cleaned_data.get('pickup_coords')
        destination_coords = cleaned_data.get('destination_coords')
        try:
            float(pickup_coords.split(',')[0]), float(pickup_coords.split(',')[1])
            float(destination_coords.split(',')[0]), float(destination_coords.split(',')[1])
        except (ValueError, IndexError, AttributeError):
            raise forms.ValidationError("Please select valid pickup and destination locations from the suggestions.")
        return cleaned_data    