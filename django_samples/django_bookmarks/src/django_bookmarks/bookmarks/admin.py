from django.contrib import admin
from django_bookmarks.bookmarks.models import Link, Bookmark, Tag, SharedBookmark, Friendship, Invitation

class LinkAdmin(admin.ModelAdmin):
	pass

class BookmarkAdmin(admin.ModelAdmin):
	list_display = ('title', 'link', 'user',)
	list_filter = ('user',)
	ordering = ('title',)
	search_fields = ('title',)

class TagAdmin(admin.ModelAdmin):
	pass

class SharedBookmarkAdmin(admin.ModelAdmin):
	pass

class FriendshipAdmin(admin.ModelAdmin):
	pass

class InvitationAdmin(admin.ModelAdmin):
	pass

admin.site.register(Link, LinkAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(SharedBookmark, SharedBookmarkAdmin)
admin.site.register(Friendship, FriendshipAdmin)
admin.site.register(Invitation, InvitationAdmin)
