# store/forms.py
from django import forms
from .models import Comment

class CommentCreateForm(forms.ModelForm):
    parent = forms.IntegerField(required=False, widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea, label='Текст комментария')

    class Meta:
        model = Comment
        fields = ['text']