from django.contrib import admin

from forum import models


class ForumVisitInline(admin.StackedInline):
    model = models.ForumVisit

class ForumUserAdmin(admin.ModelAdmin):
    inlines = [ForumVisitInline]


class PostInline(admin.TabularInline):
    model = models.Post


class TopicAdmin(admin.ModelAdmin):
    inlines = [PostInline]


admin.site.register(models.ForumUser, ForumUserAdmin)
admin.site.register(models.Category)
admin.site.register(models.Topic, TopicAdmin)
