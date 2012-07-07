import datetime
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.core import paginator
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotAllowed

from forum.models import Topic, Post, ForumUser
from forum.forms import TopicForm, PostForm, ForumUserForm
from forum.templatetags.forum import topic_list_item_row
from forum.decorators import moderator_login_required


def _api_url(request, page):
    chunks = [request.path, "?page=", str(page)]
    return "".join(chunks)

def topic_list(request):
    per_page = 40
    topics = Topic.objects.all().select_related(depth=2)\
            .order_by('-is_sticked', '-updated')
    tpaginator = paginator.Paginator(topics, per_page)

    page_num = request.GET.get('page')
    try:
        page = tpaginator.page(page_num)
    except paginator.PageNotAnInteger:
        page = tpaginator.page(1)
    except paginator.EmptyPage:
        tpaginator = paginator.Paginator(Topic.objects.none(), per_page)
        page = tpaginator.page(1)

    if 'xhr' in request.GET:
        objects = []
        for t in page.object_list:
            objects.append({
                'id': t.id,
                'html': topic_list_item_row(t, request.forum_user),
            })
        response = {
            'meta': {
                'pagination': {
                    'next': _api_url(request, page.next_page_number()),
                    'prev': _api_url(request, page.previous_page_number()),
                    'current': _api_url(request, page.number),
                },
                'per_page': per_page,
            },
            'objects': objects,
        }
        content = json.dumps(response)
        return HttpResponse(content, content_type='application/json')

    ctx = {
        'forum_user': request.forum_user,
        'topics_page': page,
        'api_url_next': _api_url(request, page.next_page_number()),
        'api_url_previous': _api_url(request, page.previous_page_number()),
    }
    return render(request, 'forum/topic/list.html', ctx)

def topic_details(request, topic_id, slug=None):
    per_page = 100
    topic = get_object_or_404(Topic.objects.select_related(), id=topic_id)
    posts = topic.post_set.all().order_by('-created')
    ppaginator = paginator.Paginator(posts, per_page)

    if request.forum_user.is_authenticated():
        request.forum_user.forum_visit.mark_visited(topic)

    page_num = request.GET.get('page')
    try:
        page = ppaginator.page(page_num)
    except paginator.PageNotAnInteger:
        page = ppaginator.page(1)
    except paginator.EmptyPage:
        page = ppaginator.page(ppaginator.num_pages)
    ctx = {
        'topic': topic,
        'posts_page': page,
        'forum_user': request.forum_user,
    }
    topic.display_count += 1
    topic.save()
    return render(request, 'forum/topic/details.html', ctx)

@login_required
def topic_create(request):
    if request.method == 'POST':
        return _topic_create_POST(request)
    ctx = {
        'forum_user': request.forum_user,
        'topic_form': TopicForm(),
        'post_form': PostForm(),
    }
    return render(request, 'forum/topic/create.html', ctx)

@transaction.commit_manually
def _topic_create_POST(request):
    commit = True
    try:
        post = Post(author=request.forum_user)
        post_form = PostForm(request.POST, instance=post)
        if post_form.is_valid():
            post = post_form.save()
            topic = Topic(author=request.forum_user, first_post=post,
                    last_post=post)
            topic_form = TopicForm(request.POST, instance=topic)
            if topic_form.is_valid():
                topic = topic_form.save()
                post.topic = topic
                post.save()
                return redirect(post.get_absolute_url())
        else:
            post_form = PostForm(request.POST)
        ctx = {
            'forum_user': request.forum_user,
            'topic_form': topic_form,
            'post_form': post_form,
        }
        return render(request, 'forum/topic/create.html', ctx)

    finally:
        if commit:
            transaction.commit()
        else:
            transaction.rollback()

@login_required
def post_create(request, topic_id, slug=None):
    # xhr
    raise NotImplementedError

@login_required
def topic_unread(request):
    per_page = 40
    topics = request.forum_user.forum_visit.unread_topics()
    topics = topics.order_by('-is_sticked', '-updated')
    tpaginator = paginator.Paginator(topics, per_page)

    page_num = request.GET.get('page')
    try:
        page = tpaginator.page(page_num)
    except paginator.PageNotAnInteger:
        page = tpaginator.page(1)
    except paginator.EmptyPage:
        tpaginator = paginator.Paginator(Topic.objects.none(), per_page)
        page = tpaginator.page(1)

    if 'xhr' in request.GET:
        objects = []
        for t in page.object_list:
            objects.append({
                'id': t.id,
                'html': topic_list_item_row(t, request.forum_user),
            })
        response = {
            'meta': {
                'pagination': {
                    'next': _api_url(request, page.next_page_number()),
                    'prev': _api_url(request, page.previous_page_number()),
                    'current': _api_url(request, page.number),
                },
                'per_page': per_page,
            },
            'objects': objects,
        }
        content = json.dumps(response)
        return HttpResponse(content, content_type='application/json')

    ctx = {
        'forum_user': request.forum_user,
        'topics_page': page,
        'api_url_next': _api_url(request, page.next_page_number()),
        'api_url_previous': _api_url(request, page.previous_page_number()),
    }
    return render(request, 'forum/topic/list_unread.html', ctx)

@login_required
def topic_mark_all_read(request):
    visit = request.forum_user.forum_visit
    visit.visited_ids = ()
    visit.visited_all = datetime.datetime.now()
    visit.save()

    if 'next' in request.GET:
        return redirect(request.GET['next'])

    referer_fallback = reverse('forum-topic-list')
    referer = request.META.get('HTTP_REFERER', referer_fallback)
    if referer == reverse('forum-topic-mark-all-read'):
        referer = referer_fallback
    return redirect(referer)

@moderator_login_required
def topic_close_toggle(request, topic_id):
    pass

@moderator_login_required
def topic_delete(request, topic_id, slug=None):
    topic = get_object_or_404(Topic, id=topic_id)
    topic.delete()
    next_uri = request.REQUEST.get('next', None)
    if not next_uri:
        next_uri = request.META.get('HTTP_REFERER', None)
        if next_uri == reverse('forum-topic-delete', [topic.id]):
            next_uri = None
    if not next_uri:
        next_uri = reverse('forum-topic-list')
    return redirect(next_uri)

@moderator_login_required
def topic_toggle_close(request, topic_id, slug=None):
    topic = get_object_or_404(Topic, id=topic_id)
    topic.is_closed = not topic.is_closed
    topic.save()
    next_uri = request.REQUEST.get('next', None)
    if not next_uri:
        next_uri = request.META.get('HTTP_REFERER', None)
        if next_uri == reverse('forum-topic-toggle-close', [topic.id]):
            next_uri = None
    if not next_uri:
        next_uri = reverse('forum-topic-list')
    return redirect(next_uri)

def user_details(request, name_or_id):
    try:
        user = get_object_or_404(ForumUser, id=int(name_or_id))
    except ValueError:
        user = get_object_or_404(ForumUser, name=name_or_id)
    ctx = {'viewed_user': user}
    return render(request, 'forum/user/details.html', ctx)

def user_edit(request, name_or_id):
    try:
        user = get_object_or_404(ForumUser, id=int(name_or_id))
    except ValueError:
        user = get_object_or_404(ForumUser, name=name_or_id)

    if request.method == 'POST':
        form = ForumUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect(user.get_absolute_url())
    else:
        form = ForumUserForm(instance=user)

    ctx = {'viewed_user': user, 'form': form}
    return render(request, 'forum/user/edit.html', ctx)
