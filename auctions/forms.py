import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Listing, Bid, Comment


class ListingForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        # ('value', 'display_name')
        ("Fashion", "Fashion"),
        ("Toys", "Toys"),
        ("Electronics", "Electronics"),
        ("Home", "Home"),
        ("Books", "Books"),
        ("Other", "Other"),
    ]
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select)

    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image", "category"]
        error_messages = {
            "image": {
                "invalid": "Please enter a valid URL (https//).",
            }
        }

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title == "":
            raise forms.ValidationError("Title cannot be empty.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if description == "":
            raise forms.ValidationError("Description cannot be empty.")
        return description

    def clean_starting_bid(self):
        starting_bid = self.cleaned_data.get("starting_bid")
        if starting_bid is None:
            raise forms.ValidationError("Starting bid cannot be empty.")
        if starting_bid < 0:
            raise forms.ValidationError("Starting bid must be positive.")
        return starting_bid

    def clean_image(self):
        url = self.cleaned_data.get("image")
        if url:
            url_pattern = (
                r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\."
                r"[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
            )
            if not re.match(url_pattern, url):
                raise ValidationError("Invalid URL format.")
        return url


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]

    def clean_amount(self):
        bid_value = self.cleaned_data.get("amount")
        if bid_value is None:
            raise forms.ValidationError("The bid value cannot be empty.")
        if bid_value <= 0:
            raise forms.ValidationError("The bid must be greater than 0.")
        return bid_value


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Share your thoughts about this auction...",
                    "maxlength": "500",
                    "style": "resize: none;",
                    "aria-label": "Comment text",
                }
            ),
        }
        labels = {
            "text": "Add a comment:",
        }
