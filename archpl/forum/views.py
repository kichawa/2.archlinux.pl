import datetime
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest

from forum.models import Topic, Post, ForumUser, Category
from forum.forms import TopicForm, PostForm, ForumUserForm
from forum.decorators import moderator_login_required
from forum.pagination import TopicPaginator, PostPaginator


def _redirect_next(request, model_or_route_name=None, args=()):
    next_uri = request.REQUEST.get('next', None)
    if not next_uri and model_or_route_name:
        try:
            next_uri = model_or_route_name.get_absolute_url()
        except AttributeError:
            next_uri = reverse(model_or_route_name, args=args)
    if not next_uri:
        next_uri = request.META.get('HTTP_REFERER', None)
    return redirect(next_uri)

def category_list(request):
    categories = Category.objects.all()
    ctx = {'categories': categories}
    return render(request, 'forum/category/list.html', ctx)

def topic_list(request):
    per_page = 40
    topics = Topic.objects.all().select_related(depth=2)\
            .order_by('-is_sticked', '-updated')
    tpaginator = TopicPaginator(topics, per_page)

    try:
        page = tpaginator.page(int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        return HttpResponseBadRequest()

    if 'xhr' in request.GET:
        response = page.as_json_ready(request)
        content = json.dumps(response)
        return HttpResponse(content, content_type='application/json')

    ctx = {
        'forum_user': request.forum_user,
        'topics_page': page,
    }
    ctx.update(page.as_json_ready_meta(request))
    return render(request, 'forum/topic/list.html', ctx)

def topic_details(request, topic_id, slug=None):
    per_page = 100
    topic = get_object_or_404(Topic.objects.select_related(), id=topic_id)
    posts = topic.post_set.all().order_by('-created')
    ppaginator = PostPaginator(posts, per_page)

    if request.forum_user.is_authenticated():
        request.forum_user.forum_visit.mark_visited(topic)

    try:
        page = ppaginator.page(int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        return HttpResponseBadRequest()

    ctx = {
        'topic': topic,
        'posts_page': page,
        'forum_user': request.forum_user,
        'post_form': PostForm(),
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
                for category in topic.categories.all():
                    category.topic_count = category.topic_set.all().count()
                    category.post_count = Post.objects\
                            .filter(topic__in=category.topic_set.all()).count()
                    category.save()
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
def topic_unread(request):
    per_page = 40
    topics = request.forum_user.forum_visit.unread_topics()
    topics = topics.order_by('-is_sticked', '-updated')
    tpaginator = TopicPaginator(topics, per_page)

    try:
        page = tpaginator.page(int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        return HttpResponseBadRequest()

    if 'xhr' in request.GET:
        response = page.as_json_ready(request)
        content = json.dumps(response)
        return HttpResponse(content, content_type='application/json')

    ctx = {
        'forum_user': request.forum_user,
        'topics_page': page,
    }
    ctx.update(page.as_json_ready_meta(request))
    return render(request, 'forum/topic/list_unread.html', ctx)

@login_required
def topic_mark_all_read(request):
    visit = request.forum_user.forum_visit
    visit.visited_ids = ()
    visit.visited_all = datetime.datetime.now()
    visit.save()
    return _redirect_next(request, 'forum-topic-list')

@moderator_login_required
def topic_close_toggle(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    topic.is_closed = not topic.is_closed
    topic.save()
    return _redirect_next(request, 'forum-topic-list')

@moderator_login_required
def topic_delete(request, topic_id, slug=None):
    topic = get_object_or_404(Topic, id=topic_id)
    topic.delete()
    return _redirect_next(request, 'forum-topic-list')

@moderator_login_required
def topic_toggle_close(request, topic_id, slug=None):
    topic = get_object_or_404(Topic, id=topic_id)
    topic.is_closed = not topic.is_closed
    topic.save()
    return _redirect_next(request, topic)

@moderator_login_required
def topic_toggle_sticky(request, topic_id, slug=None):
    topic = get_object_or_404(Topic, id=topic_id)
    topic.is_sticked = not topic.is_sticked
    topic.save()
    return _redirect_next(request, topic)

def topic_redirect_to_solving_post(request, topic_id, slug=None):
    topic = get_object_or_404(Topic, id=topic_id, solved_by__isnull=False)
    post = topic.post_set.get(is_solving=True)
    return redirect(post.get_absolute_url())

@transaction.commit_on_success
def post_is_solving(request, topic_id=None, slug=None, post_id=None):
    post = get_object_or_404(Post, id=post_id, topic__id=topic_id)
    topic = post.topic
    if not topic.is_solved:
        topic.solved_by = post.id
        topic.save()
        post.is_solving = True
        post.save()
    return _redirect_next(request, post)

@login_required
@transaction.commit_on_success
def post_create(request, topic_id, slug=None):
    topic = get_object_or_404(Topic, id=topic_id, is_closed=False)
    is_xhr = bool(request.REQUEST.get('xhr'))
    post = Post(topic=topic, author=request.forum_user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()

            # update counters
            topic.post_count = topic.post_set.all().count()
            topic.updated = post.created
            topic.save()
            for category in topic.categories.all():
                category.topic_count = category.topic_set.all().count()
                category.post_count = Post.objects\
                        .filter(topic__in=category.topic_set.all()).count()
                category.save()

            if is_xhr:
                return {
                    'status': 'ok',
                    'saved': True,
                    'url': post.get_absolute_url()
                }
            return _redirect_next(request, post)
        if is_xhr:
            return {
                'status': 'ok',
                'saved': False,
                'errors': form.errors(),
            }
    else:
        form = PostForm()

    ctx = {'post_form': form, 'topic': topic}
    return render(request, 'forum/post/create.html', ctx)

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

@login_required
def user_menu_position_toggle(request):
    user = request.forum_user
    user.menu_always_on_top = not user.menu_always_on_top
    user.save()
    return _redirect_next(request)
