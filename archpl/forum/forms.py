from django import forms

from forum.models import Post, Topic, ForumUser


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('title', 'categories')


class PostForm(forms.ModelForm):
    markup_lang = forms.ChoiceField(widget=forms.RadioSelect,
            choices=Post.MARKUP_CHOICES, initial=Post.MARKUP_CHOICES[0][0])

    class Meta:
        model = Post
        fields = ('content', 'markup_lang')


class ForumUserForm(forms.ModelForm):
    class Meta:
        model = ForumUser
        fields = ('name', 'avatar')
