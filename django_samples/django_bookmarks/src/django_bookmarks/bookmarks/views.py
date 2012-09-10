import smtplib
from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from django_bookmarks.bookmarks.forms import RegistrationForm, BookmarkSaveForm, SearchForm,\
	FriendInviteForm
from django_bookmarks.bookmarks.models import Link, Bookmark, Tag, SharedBookmark, Friendship, Invitation

ITEM_PER_PAGE = 5

def main_page(request):
	shared_bookmarks = SharedBookmark.objects.order_by('-date')[:10]
	variables = RequestContext(request, {
		'shared_bookmarks': shared_bookmarks
	})
	return render_to_response('main_page.html', variables)

def user_page(request, username):
	user = get_object_or_404(User, username=username)
	if request.user.is_authenticated():
		is_friend = Friendship.objects.filter(
			from_friend=request.user,
			to_friend=user
		)
	else:
		is_friend = False;
	query_set = user.bookmark_set.order_by('-id')
	paginator = Paginator(query_set, ITEM_PER_PAGE)
	try:
		page_number = int(request.GET['page'])
	except (KeyError, ValueError):
		page_number = 1
	try:
		page = paginator.page(page_number)
	except InvalidPage:
		raise Http404
	bookmarks = page.object_list
	variables = RequestContext(request, {
		'username': username,
		'bookmarks': bookmarks,
		'show_tags': True,
		'show_edit': username == request.user.username,
		'show_paginator': paginator.num_pages > 1,
		'has_prev': page.has_previous(),
		'has_next': page.has_next(),
		'page': page_number,
		'pages': paginator.num_pages,
		'next_page': page_number + 1,
		'prev_page': page_number - 1,
		'is_friend': is_friend
	})
	return render_to_response('user_page.html', variables)

def logout_page(request):
	logout(request)
	return HttpResponseRedirect('/')

def register_page(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(
				username=form.cleaned_data['username'],
				email=form.cleaned_data['email'],
				password=form.cleaned_data['password1']
			)
			if 'invitation' in request.session:
				# Retrieve the invitation object
				invitation = Invitation.objects.get(id = request.session['invitation'])
				# Create the friendship
				friendship = Friendship(
					from_friend = user,
					to_friend = invitation.sender
				)
				friendship.save()
				# Create reverse friendship
				friendship = Friendship(
					from_friend = invitation.sender,
					to_friend = user
				)
				friendship.save()
				# Delete invitation in DB
				invitation.delete()
				# Clean session object
				del request.session['invitation']
			return HttpResponseRedirect('/register/success/')
	else:
		form = RegistrationForm()
	variables = RequestContext(request, { 'form': form })
	return render_to_response('registration/register.html', variables)

@login_required
def bookmark_save_page(request):
	ajax = 'ajax' in request.GET
	if request.method == 'POST':
		form = BookmarkSaveForm(request.POST)
		if form.is_valid():
			bookmark = _bookmark_save(request, form)
			if ajax:
				variables = RequestContext(request, {
					'bookmarks': [bookmark],
					'show_edit': True,
					'show_tags': True
				})
				return render_to_response('bookmark_list.html', variables)
			else:
				return HttpResponseRedirect('/user/%s/' % request.user.username)
		else:
			if ajax:
				return HttpResponse(u'failure')
	elif 'url' in request.GET:
		url = request.GET['url']
		title = ''
		tags = ''
		try:
			link = Link.objects.get(url=url)
			bookmark = Bookmark.objects.get(link=link, user=request.user)
			title = bookmark.title
			tags = ' '.join(
				tag.name for tag in bookmark.tag_set.all()
			)
		except (Link.DoesNotExist, Bookmark.DoesNotExist):
			pass
		form = BookmarkSaveForm({
			'url' : url,
			'title' : title,
			'tags' : tags
		})
	else:
		form = BookmarkSaveForm()
	variables = RequestContext(request, {'form':form})
	if ajax:
		return render_to_response('bookmark_save_form.html', variables)
	else:
		return render_to_response('bookmark_save.html', variables)

def _bookmark_save(request, form):
	# Create or get a link
	link, dummy = Link.objects.get_or_create(url = form.cleaned_data['url'])
	# Create or get a bookmark
	bookmark, created = Bookmark.objects.get_or_create(user=request.user, link=link)
	# Update bookmark title
	bookmark.title = form.cleaned_data['title']
	# If the bookmark is being updated, clear old tag list
	if not created:
		bookmark.tag_set.clear()
	# Create tag list
	tag_names = form.cleaned_data['tags'].split()
	for tag_name in tag_names:
		tag, dummy = Tag.objects.get_or_create(name=tag_name)
		bookmark.tag_set.add(tag)
	# Share the bookmark if requested
	if form.cleaned_data['share']:
		shared, created = SharedBookmark.objects.get_or_create(bookmark=bookmark)
		if created:
			shared.users_voted.add(request.user)
			shared.save()
	# Save the bookmark to database
	bookmark.save()
	return bookmark

def tag_page(request, tag_name):
	tag = get_object_or_404(Tag, name=tag_name)
	bookmarks = tag.bookmarks.order_by('-id')
	variables = RequestContext(request, {
		'bookmarks': bookmarks,
		'tag_name': tag_name,
		'show_tags': True,
		'show_user': True,
	})
	return render_to_response('tag_page.html', variables)

def tag_cloud_page(request):
	MAX_WEIGHT = 5
	tags = Tag.objects.order_by('name')
	# Calculate the min & max
	min_count = max_count = tags[0].bookmarks.count()
	for tag in tags:
		tag.count = tag.bookmarks.count()
		if tag.count < min_count:
			min_count = tag.count
		if max_count < tag.count:
			max_count = tag.count
	# Calculate count range, avoiding dividing by zero
	range = float(max_count - min_count)
	if range == 0.0:
		range = 1.0
	# Calculate tags weights
	for tag in tags:
		tag.weight = int(MAX_WEIGHT * (tag.count - min_count) / range)
	variables = RequestContext(request, {
		'tags': tags
	})
	return render_to_response('tag_cloud_page.html', variables)

def ajax_tag_autocomplete(request):
	if 'term' in request.GET:
		tags = Tag.objects.filter(
			name__istartswith = request.GET['term']
		)[:10]
		return HttpResponse(u'["%s"]' % ('","'.join(tag.name for tag in tags)))
	return HttpResponse()

def search_page(request):
	form = SearchForm()
	bookmarks = []
	show_results = False
	if 'query' in request.GET:
		show_results = True
		query = request.GET['query'].strip()
		if query:
			keywords = query.split()
			q = Q()
			for keyword in keywords:
				q = q & Q(title__icontains=keyword)
			form = SearchForm({'query': query})
			bookmarks = Bookmark.objects.filter(q)[:10]
	variables = RequestContext(request, {
		'form': form,
		'bookmarks': bookmarks,
		'show_results': show_results,
		'show_tags': True,
		'show_user': True
	})
	if request.GET.has_key('ajax'):
		return render_to_response('bookmark_list.html', variables)
	else:
		return render_to_response('search.html', variables)

@login_required
def bookmark_vote_page(request):
	if 'id' in request.GET:
		try:
			id = request.GET['id']
			shared_bookmark = SharedBookmark.objects.get(id=id)
			user_voted = shared_bookmark.users_voted.filter(username=request.user.username)
			if not user_voted:
				shared_bookmark.votes += 1
				shared_bookmark.users_voted.add(request.user)
				shared_bookmark.save()
		except SharedBookmark.DoesNotExist:
			raise Http404('Bookmark not found.')
	if 'HTTP_REFERER' in request.META:
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	return HttpResponseRedirect('/')

def popular_bookmark_page(request):
	today = datetime.today()
	yesterday = today - timedelta(1)
	shared_bookmarks = SharedBookmark.objects.filter(
		date__gt = yesterday
	)
	shared_bookmarks = shared_bookmarks.order_by('-votes')[:10]
	variables = RequestContext(request, {
		'shared_bookmarks': shared_bookmarks
	})
	return render_to_response('popular_tag.html', variables)

def bookmark_page(request, bookmark_id):
	shared_bookmark = get_object_or_404(SharedBookmark, id=bookmark_id)
	variables = RequestContext(request, {'shared_bookmark': shared_bookmark})
	return render_to_response('bookmark_page.html', variables)

def friends_page(request, username):
	user = get_object_or_404(User, username=username)
	friends = [friendship.to_friend for friendship in user.friend_set.all()]
	friend_bookmarks = Bookmark.objects.filter(
		user__in = friends
	).order_by('-id')
	variables = RequestContext(request, {
		'username': username,
		'friends': friends,
		'bookmarks': friend_bookmarks[:10],
		'show_tags': True,
		'show_user': True
	})
	return render_to_response('friends_page.html', variables)

@login_required
def friend_add(request):
	if 'username' in request.GET:
		friend = get_object_or_404(User, username=request.GET['username'])
		friendship = Friendship(
			from_friend=request.user,
			to_friend=friend
		)
		try:
			friendship.save()
			request.user.message_set.create(
				message=u'%s was added to your friend list.' % friend.username
			)
		except:
			request.user.message_set.create(
				message=u'%s is already one of your friends.' % friend.username
			)
# To add the reverse friendship directly, uncomment the lines below
#		friendship = Friendship(
#			from_friend=friend,
#			to_friend=request.user
#		)
#		friendship.save()
		return HttpResponseRedirect('/friends/%s/' % request.user.username)
	else:
		raise Http404

@login_required
def friend_invite(request):
	if request.method == 'POST':
		form = FriendInviteForm(request.POST)
		if form.is_valid():
			invitation = Invitation(
				name = form.cleaned_data['name'],
				email = form.cleaned_data['email'],
				code = User.objects.make_random_password(20),
				sender = request.user
			)
			invitation.save()
			try:
				invitation.send()
				request.user.message_set.create(
					message=_(u'An invitation has been sent to %(email)s.') % { 'email': invitation.email}
				)
			except smtplib.SMTPException:
				request.user.message_set.create(
					message=_(u'An error happened when sending the invitation.')
				)
			return HttpResponseRedirect('/friend/invite/')
	else:
		form = FriendInviteForm()
	variables = RequestContext(request, {'form': form})
	return render_to_response('friend_invite.html', variables)

def friend_accept(request, code):
	invitation = get_object_or_404(Invitation, code__exact=code)
	request.session['invitation'] = invitation.id
	return HttpResponseRedirect('/register/')
