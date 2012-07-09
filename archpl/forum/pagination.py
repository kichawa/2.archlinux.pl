from django.core import paginator

from forum.templatetags.forum import topic_list_item_row


def _api_url(request, page):
    if not page:
        return None
    chunks = [request.path, "?page=", str(page)]
    return "".join(chunks)


class Page(paginator.Page):
    def as_json_ready_meta(self, request):
        data = {
            'pagination': {
                'next': None,
                'prev': None,
                'current': self.number,
                'per_page': self.paginator.per_page,
            },
        }
        if self.has_next():
            data['pagination']['next'] = self.next_page_number()
        if self.has_previous():
            data['pagination']['prev'] = self.previous_page_number()
        return data

    def as_json_ready_objects(self, request):
        return ()

    def as_json_ready(self, request):
        return {
            'meta': self.as_json_ready_meta(request),
            'objects': self.as_json_ready_objects(request),
        }


class Paginator(paginator.Paginator):
    page_cls = Page

    def page(self, number):
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return self.page_cls(self.object_list[bottom:top], number, self)


class TopicPage(Page):
    def as_json_ready_objects(self, request):
        json_ready = []
        for t in self.object_list:
            raw = {
                'id': t.id,
                'html': topic_list_item_row(t, request.forum_user),
            }
            json_ready.append(raw)
        return json_ready


class TopicPaginator(Paginator):
    page_cls = TopicPage



class PostPage(Page):
    def as_json_ready_objects(self, request):
        raise NotImplementedError


class PostPaginator(Paginator):
    page_cls = PostPage
