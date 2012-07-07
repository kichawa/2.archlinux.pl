from django.utils.functional import SimpleLazyObject

from forum.models import ForumUser, AnonymousForumUser


class ForumAuthenticationMiddleware(object):
    def process_request(self, request):
        request.forum_user = SimpleLazyObject(_get_forum_user(request))


def _get_forum_user(request):
    def get_user():
        if not hasattr(request, '_cached_forum_user'):
            if request.user.is_anonymous():
                u = AnonymousForumUser()
            else:
                try:
                    u = ForumUser.objects.get(user=request.user)
                except ForumUser.DoesNotExist:
                    u = AnonymousForumUser()
            request._cached_forum_user = u
        return request._cached_forum_user

    return get_user
