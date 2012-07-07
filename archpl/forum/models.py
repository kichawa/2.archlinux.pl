import datetime
import json

from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse



class AnonymousForumUser(AnonymousUser):
    pass


class ForumUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    avatar = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=32, unique=True)
    is_moderator = models.BooleanField(default=False)

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def username(self):
        if not hasattr(self, '_username'):
            self._username = self.name
            if not self._username:
                user = self.user.username
                self._username = user.get_full_name()
            if not self._username:
                self._username = user.username
        return self._username

    @property
    def forum_visit(self):
        if not hasattr(self, '_forum_visit'):
            visit, _ = ForumVisit.objects.get_or_create(user=self,
                    defaults={'visited_all': datetime.datetime.now()})
            self._forum_visit = visit
        return self._forum_visit

    def __unicode__(self):
        return "{}: {}".format(self.id, self.username())

    @models.permalink
    def get_absolute_url(self):
        return ('forum-user-details', [self.name or self.id])


class ForumVisit(models.Model):
    user = models.ForeignKey(ForumUser, unique=True)
    visited_all = models.DateTimeField()
    _visited_ids = models.TextField(db_column='visited_ids', blank=True)

    @property
    def visited_ids(self):
        if not self._visited_ids:
            return set([])
        return set(json.loads(self._visited_ids))

    @visited_ids.setter
    def visited_ids(self, value):
        self._visited_ids = json.dumps(tuple(value))

    def mark_visited(self, topic):
        if self.visited_all < topic.last_post.created:
            ids = self.visited_ids
            ids.add(int(topic.id))
            self.visited_ids = ids
            self.save()
        return self

    def unread_topics(self):
        return Topic.objects.select_related(depth=2)\
                    .filter(updated__gte=self.visited_all)\
                    .exclude(id__in=self.visited_ids)


class Category(models.Model):
    name = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True)
    post_count = models.PositiveIntegerField(default=0)
    topic_count = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.name


class Topic(models.Model):
    title = models.CharField(max_length=128)
    author = models.ForeignKey(ForumUser)
    categories = models.ManyToManyField(Category)
    updated = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)
    is_sticked = models.BooleanField(default=False)
    is_solved = models.BooleanField(default=False)

    display_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=1)
    first_post = models.ForeignKey('Post', related_name='_topic_first')
    last_post = models.ForeignKey('Post', related_name='_topic_last')

    @models.permalink
    def get_absolute_url(self):
        slug = slugify(self.title)
        return ('forum-topic-details', [self.id, slug])

    def __unicode__(self):
        return "{} by {}: {}".format(self.id, self.author.username, self.title)


class Post(models.Model):
    MARKUP_CHOICES = (
        ('markdown', 'Markdown'),
        ('texttile', 'Texttile'),
        ('bbcode', 'BBCode'),
    )
    topic = models.ForeignKey(Topic, null=True)
    author = models.ForeignKey(ForumUser)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_solving = models.BooleanField(default=False)
    #markup_lang = models.CharField(max_length=8, choices=MARKUP_CHOICES)
    markup_lang = 'bbcode'

    def get_absolute_url(self):
        slug = slugify(self.topic.title)
        url = reverse('forum-topic-details', [self.topic.id, slug])
        return '{}#post-{}'.format(url, self.id)

    def __unicode__(self):
        return "Post {} by {}".format(self.id, self.author.username)
