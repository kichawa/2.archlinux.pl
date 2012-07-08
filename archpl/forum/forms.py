from django import forms

from forum.models import Post, Topic, ForumUser


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('title', 'categories')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content', 'markup_lang')


class ForumUserForm(forms.ModelForm):
    class Meta:
        model = ForumUser
        fields = ('name', 'avatar')
