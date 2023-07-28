from django import forms

from .models import Comments


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        exclude = ["post"]
        labels = {
            "user_name" : "Your Name",
            "user_email" : "Your Email",
            "text" : "Your Comment"
        }
