# store/templatetags/comment_extras.py
from django import template

register = template.Library()

@register.filter
def is_liked_by(comment, user):
    if user.is_anonymous:
        return False
    return comment.is_liked_by(user)