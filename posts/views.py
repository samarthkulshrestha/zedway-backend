from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import JsonResponse
from posts.models import Post, Like, Comment, PostReport, CommentReport, Tag
from django.contrib.auth.models import User
import os
import re
from notifications.signals import notify
import logging


def new_type(request):
    if request.method == 'POST':
        type = request.POST['format']
        if type == 'IMG':
            return render(request, 'post_img.html')
        if type == 'VID':
            return render(request, 'post_vid.html')
        if type == 'AU':
            return render(request, 'post_au.html')
        if type == 'TXT':
            return render(request, 'post_txt.html')


def newPost(request):
    if request.method == 'POST':
        title = request.POST['title']
        desc = request.POST['desc']
        type = request.POST['type']
        is_safe = request.POST['is_safe']
        creator = request.user
        explore = request.POST['explore']
        tags = request.POST['tags']
        tags = re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))#([A-Za-z]+[A-Za-z0-9-_]+)', tags)
        if type == 'TXT':
            post = Post.objects.create(title=title, desc=desc, type=type, is_safe=is_safe, creator=creator, explore=explore)
        else:
            file = request.FILES['file']
            post = Post.objects.create(title=title, desc=desc, file=file, type=type, is_safe=is_safe, creator=creator, explore=explore)
        post.save()
        for i in tags:
            tag = '#' + str(i)
            obj, created = Tag.objects.get_or_create(tag=tag)
            obj.posts.add(post)
        if type == 'IMG':
            return render(request, 'crop.html', {'post': post})
        return redirect('/')
    else:
        return redirect('/')


def like_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)

        if user in post_obj.liked.all():
            post_obj.liked.remove(user)
        else:
            post_obj.liked.add(user)
            notify.send(user, verb='liked', action_object=post_obj, recipient=post_obj.creator)

        like, created = Like.objects.get_or_create(user=user, post_id=post_id)

        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'

        like.save()

    url = '/posts/' + str(post_obj.slug)

    return redirect(url)


def ajax_like_post(request):
    user = request.user
    status = request.GET.get('status', None)
    post_id = request.GET.get('post_id', None)
    post_obj = Post.objects.get(id=post_id)

    if user in post_obj.liked.all():
        post_obj.liked.remove(user)
        status = 'unliked'
    else:
        post_obj.liked.add(user)
        notify.send(user, verb='liked', action_object=post_obj, recipient=post_obj.creator)
        status = 'liked'

    like, created = Like.objects.get_or_create(user=user, post_id=post_id)

    if not created:
        if like.value == 'Like':
            like.value = 'Unlike'
        else:
            like.value = 'Like'

    like.save()

    data = {
        'status': status,
        'count': post_obj.liked.all().count(),
        'post_id': post_id,
    }

    return JsonResponse(data)


def view_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.all()
    type = post.type

    if request.method == 'POST':
        body = request.POST['body']
        mentions = re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)', body)
        user = request.user
        comment = Comment.objects.create(post=post, user=user, body=body)
        comment.post = post
        comment.save()
        if mentions is not None:
            for i in mentions:
                uname = '@' + str(i)
                users = User.objects.all()
                if uname in users:
                    recipient = User.objects.get(username=uname)
                    notify.send(user, verb='mentioned you in a view for', action_object=post, recipient=recipient)
                else:
                    pass
        notify.send(user, verb='posted a view for', action_object=post, recipient=post.creator)
        url = '/posts/' + str(slug)
        return redirect(url)
    if type == 'IMG':
        return render(request, 'img_view.html', {'comments': comments, 'post': post})
    elif type == 'AU':
        return render(request, 'au_view.html', {'comments': comments, 'post': post})
    elif type == 'VID':
        return render(request, 'vid_view.html', {'comments': comments, 'post': post})
    else:
        return render(request, 'txt_view.html', {'comments': comments, 'post': post})


def delete_post(request, slug):
    post_to_delete = Post.objects.get(slug=slug)
    file = post_to_delete.file
    print(file)
    post_to_delete.delete()
    os.system("rm -rf ~/Dev/zedway/media/" + str(file))
    return redirect('/')


def report_post(request, slug):
    if request.method == 'POST':
        message = request.POST['message']
        post_to_report = Post.objects.get(slug=slug)
        reporting_user = request.user
        report = PostReport.objects.create(message=message)
        report.save()
        report.post_to_report.add(post_to_report)
        report.reporting_user.add(reporting_user)
        subject = str(reporting_user) + ' reported ' + str(post_to_report)
        message = render_to_string('email/report_email.html', {
            'message': message
        })
        to_email = 'rai.ananya2005@gmail.com'
        email = EmailMessage(
            subject, message, to=[to_email]
        )
        email.send()
        return render(request, 'report_sent.html')
    else:
        return render(request, 'report.html')


def report_comment(request, id, slug):
    if request.method == 'POST':
        message = request.POST['message']
        comment_to_report = Comment.objects.get(id=id)
        reporting_user = request.user
        report = CommentReport.objects.create(message=message)
        report.save()
        report.comment_to_report.add(comment_to_report)
        report.reporting_user.add(reporting_user)
        subject = str(reporting_user) + ' reported ' + str(comment_to_report)
        message = render_to_string('email/report_email.html', {
            'message': message
        })
        to_email = 'rai.ananya2005@gmail.com'
        email = EmailMessage(
            subject, message, to=[to_email]
        )
        email.send()
        return render('report_sent.html')
    else:
        return render(request, 'report.html')


def liked_by(request, slug):
    post = Post.objects.get(slug=slug)
    liked = post.liked.all()
    return render(request, 'likes.html', {'liked': liked})
