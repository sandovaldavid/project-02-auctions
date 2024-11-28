from decimal import InvalidOperation, Decimal

from django import forms
from django.core.exceptions import ValidationError

from .models import Listing, Bid
import re

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']
        error_messages = {
            'image': {
                'invalid': 'Please enter a valid URL (https//).',
            }
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title == "":
            raise forms.ValidationError("Title cannot be empty.")
        if Listing.objects.filter(title=title).exists():
            raise forms.ValidationError("This title is already taken.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description == "":
            raise forms.ValidationError("Description cannot be empty.")
        return description

    def clean_starting_bid(self):
        starting_bid = self.cleaned_data.get('starting_bid')
        if starting_bid is None:
            raise forms.ValidationError("Starting bid cannot be empty.")
        if starting_bid < 0:
            raise forms.ValidationError("Starting bid must be positive.")
        return starting_bid

    def clean_image(self):
        url = self.cleaned_data.get('image')
        if url:
            url_pattern = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
            if not re.match(url_pattern, url):
                raise ValidationError("Invalid URL format.")
        return url

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

    def clean_amount(self):
        bid_value = self.cleaned_data.get("amount")
        print(bid_value)
        if bid_value is None:
            raise forms.ValidationError("The bid value cannot be empty.")
        if bid_value <= 0:
            raise forms.ValidationError("The bid must be greater than 0.")
        return bid_value