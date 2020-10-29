from django.contrib import admin
from posts.models import Post, Like, Comment

# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug',)
    search_fields = ['title', 'desc']
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Post, PostAdmin)
admin.site.register(Like)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


admin.site.register(Comment)
