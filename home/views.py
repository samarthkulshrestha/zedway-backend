from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import UserProfile
from django.contrib.auth.models import User
from posts.models import Post, Tag
from django.core.files import File
from PIL import Image


def home(request):
    self = request.user
    if self.is_authenticated is True:
        self = self.userprofile
        posts = UserProfile.get_user_feed(self)
        return render(request, 'home.html', {'posts': posts})
    else:
        return redirect('/land')


def land(request):
    return render(request, "land.html")


def explore(request):
    if request.user.userprofile.age >= 16:
        posts = Post.objects.filter(explore=True).order_by('created_on')
        return render(request, 'explore.html', {'posts': posts})
    else:
        posts = Post.objects.filter(explore=True, is_safe=True).order_by('created_on')
        return render(request, 'explore.html', {'posts': posts})


def delete_notifs(request):
    user = request.user
    user.notifications.mark_all_as_read()
    url = "/accounts/" + str(user.userprofile.slug)
    return redirect(url)


def search(request):
    if request.method == 'POST':
        keyword = str(request.POST['keyword'])
        if keyword[0] == '@':
            qs_u = User.objects.all()
            qs_f_n = qs_u.filter(first_name__icontains=keyword)
            qs_l_n = qs_u.filter(last_name__icontains=keyword)
            qs_un = qs_u.filter(username__icontains=keyword)
            qs_users = qs_f_n | qs_l_n | qs_un
            return render(request, 'search.html', {'users': qs_users})
        elif keyword[0] == '#':
            l = len(keyword)
            keyword = keyword[1:l]
            url = '/hashtags/' + str(keyword)
            return redirect(url)
        else:
            qs_u = User.objects.all()
            qs_p = Post.objects.all()
            qs_f_n = qs_u.filter(first_name__icontains=keyword)
            qs_l_n = qs_u.filter(last_name__icontains=keyword)
            qs_un = qs_u.filter(username__icontains=keyword)
            qs_tit = qs_p.filter(title__icontains=keyword)
            qs_users = qs_f_n | qs_l_n | qs_un
            return render(request, 'search.html', {'users': qs_users, 'posts': qs_tit})
    elif request.method == 'GET':
        return render(request, 'search.html')


def crop_post(request, pk):
    if request.method == 'POST':
        post = Post.objects.get(pk=pk)
        x = request.POST['x']
        y = request.POST['y']
        w = request.POST['w']
        h = request.POST['h']
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)
        print(x)
        image = Image.open(post.file)
        image = image.crop((x, y, w+x, h+y))
        image.save(post.file.path)
        post.file = post.file.name
        post.save(update_fields=["file"])
        url = '/posts/' + str(post.slug)
        return redirect(url)
    else:
        return redirect('/')


def crop_profile(request):
    if request.method == 'POST':
        user = request.user
        prev_path = request.POST['prev_path'] 
        x = request.POST['x']
        y = request.POST['y']
        w = request.POST['w']
        h = request.POST['h']
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)
        image = Image.open(user.userprofile.image)
        image = image.crop((x, y, w+x, h+y))
        image = image.resize((700, 700), Image.ANTIALIAS)
        image.save(user.userprofile.image.path)
        user.userprofile.image = user.userprofile.image.name
        user.userprofile.save(update_fields=["image"])
        return redirect(prev_path)
    else:
        return redirect('/')


def about(request):
    return render(request, 'aboutus.html')


def contactus(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
    return render(request, 'contactus.html')


def cookies_policy(request):
    return render(request, 'cookiespolicy.html')


def privacy_policy(request):
    return render(request, 'privacypolicy.html')


def security_policy(request):
    return render(request, 'securitypolicy.html')


def terms_of_use(request):
    return render(request, 'termsofuse.html')


def community_guidelines(request):
    return render(request, 'guidelines.html')


def update_img_set(request):
    if request.method == 'POST':
        user = request.user
        path = '/accounts/settings/'
        file = request.FILES['image']
        user.userprofile.image = file
        user.userprofile.save(update_fields=['image'])
        return render(request, 'crop_profile.html', {'user_profile': user, 'prev_path': path})
    else:
        path = '/accounts/settings/'
        return render(request, 'upload_profile_pic.html', {'prev_path': path})



def update_img_sign2(request):
    if request.method == 'POST':
        user = request.user
        path = '/accounts/update/'
        file = request.FILES['image']
        user.userprofile.image = file
        user.userprofile.save(update_fields=['image'])
        return render(request, 'crop_profile.html', {'user_profile': user, 'prev_path': path})
    else:
        path = '/accounts/update/'
        return render(request, 'upload_profile_pic.html', {'prev_path': path})


def hashtag(request, tag):
    word = tag
    tag = '#' + str(tag)
    obj, created = Tag.objects.get_or_create(tag=tag)
    qs_p = obj.posts.all() 
    all_f = obj.followers.all()
    return render(request, 'hashtag.html', {'qs_posts': qs_p, 'hashtag': tag, 'word': word, 'all_f': all_f})


def follow_hashtag(request, tag):
    user = request.user
    s_tag = '#' + tag
    tag = Tag.objects.get(tag=s_tag)
    if tag in user.userprofile.following_tags.all():
        user.userprofile.following_tags.remove(tag)
        tag.followers.remove(user)
    else:
        user.userprofile.following_tags.add(tag)
        tag.followers.add(user)
    l = len(s_tag)
    tag = s_tag[1:l]
    return redirect('/hashtags/' + str(tag))
