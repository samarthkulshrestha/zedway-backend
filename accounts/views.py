import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from accounts.tokens import account_activation_token
from django.utils.encoding import force_text
from django.core.mail import EmailMessage
from accounts.models import UserProfile
from .models import UserReport
from django.http import HttpResponse
from datetime import date, datetime
from notifications.signals import notify
from posts.models import Post


def register(request, backend='django.contrib.auth.backends.ModelBackend'):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = '@' + str(request.POST['username'])
        email = request.POST['email']
        password = request.POST['password']
        c_password = request.POST['c_password']

        if password == c_password:

            if User.objects.filter(username=username).exists():
                messages.info(request, 'An account with that username already exists.')
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.info(request, 'An account is already registered with that email.')
                return redirect('register')

            elif first_name == "" or username == "" or email == "" or password == "" or c_password == "":
                messages.error(request, 'Please fill in all the fields.')
                return redirect('register')

            else:
                user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                subject = 'Activate Your Zedway Account'
                message = render_to_string('email/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = user.email
                email = EmailMessage(
                    subject, message, to=[to_email]
                )
                email.send()
                return render(request, 'email_sent.html')

        else:
            messages.info(request, 'The passwords don\'t match.')
            return redirect('register')
        return redirect('/')

    else:
        return render(request, 'signup.html')


def login(request, backend='django.contrib.auth.backends.ModelBackend'):
    if request.method == 'POST':
        inp = request.POST['username']
        password = request.POST['password']
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if(re.search(regex, inp)):
            UserModel = get_user_model()
            u = UserModel.objects.get(email=inp)
            username = str(u.username)
        else:
            username = '@' + str(inp)

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'The entered information is incorrect.')
            return redirect('/accounts/login')

    else:
        return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect('/')


class ActivateAccount(View):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.email_confirmed = True
            user.save()
            auth.login(request, user)
            messages.success(request, ('Your account has been confirmed.'))
            return redirect('/accounts/update/')
        else:
            messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('/accounts/register/')


def update(request):
    if request.method == 'POST':
        user = request.user
        user_id = User.objects.get(username=user).pk
        bio = request.POST['bio']
        accent1 = request.POST['accent1']
        accent2 = request.POST['accent2']
        birth_date = datetime.strptime(request.POST['birth_date'], '%Y-%m-%d')

        def calculate_age(birth_date):
            today = date.today()
            return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        age = calculate_age(birth_date)
        user_profile = user.userprofile
        user_profile.bio = bio
        user_profile.accent1 = accent1
        user_profile.accent2 = accent2
        user_profile.birth_date = birth_date
        user_profile.age = age
        user_profile.save(update_fields=['bio', 'accent1', 'accent2', 'birth_date', 'age'])
        messages.success(request, ('Your account was successfully created. You can now sign in to your account'))
        return redirect('/accounts/login/')

    else:
        return render(request, 'updateaccount.html')


def view_profile(request, slug):
    user_profile = get_object_or_404(UserProfile, slug=slug)
    user = user_profile.user
    posts = Post.objects.filter(creator=user).order_by('created_on')
    return render(request, 'view_profile.html', {'user': user, 'posts': posts})


def follow(request, slug):
    user_to_follow = get_object_or_404(UserProfile, slug=slug)
    user = request.user
    all_followers = user_to_follow.followers.all()
    if user in all_followers:
        user_to_follow.followers.remove(user)
        user.userprofile.following.remove(user_to_follow.user)
    else:
        if user not in user_to_follow.blocked.all():
            user_to_follow.followers.add(user)
            notify.send(user, verb='followed', action_object=user_to_follow.user, recipient=user_to_follow.user)
            user.userprofile.following.add(user_to_follow.user)
    user_to_follow.save()
    url = '/accounts/' + str(slug)
    return redirect(url)


def report_user(request, slug):
    if request.method == 'POST':
        message = request.POST['message']
        user_to_report = UserProfile.objects.get(slug=slug)
        user_to_report = user_to_report.user
        reporting_user = request.user
        report = UserReport.objects.create(message=message)
        report.save()
        report.user_to_report.add(user_to_report)
        report.reporting_user.add(reporting_user)
        subject = str(reporting_user) + ' reported ' + str(user_to_report)
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


def block_user(request, slug):
    user_to_block = get_object_or_404(UserProfile, slug=slug)
    user_to_block = user_to_block.user
    user = request.user
    blocked = user.userprofile.blocked.all()
    if user_to_block in blocked:
        user.userprofile.blocked.remove(user_to_block)
    else:
        if user_to_block in user.userprofile.followers.all():
            user.userprofile.followers.remove(user_to_block)
            user_to_block.userprofile.following.remove(user)
        elif user in user_to_block.userprofile.followers.all():
            user_to_block.userprofile.followers.remove(user)
            user.userprofile.following.remove(user_to_block)
        user.userprofile.blocked.add(user_to_block)
    user.save()
    url = '/accounts/' + str(user_to_block.userprofile.slug)
    return redirect(url)


def remove_follower(request, slug, pk):
    user_to_remove = get_object_or_404(User, pk=pk)
    user = request.user
    if user_to_remove in user.userprofile.followers.all():
        user.userprofile.followers.remove(user_to_remove)
        user_to_remove.userprofile.following.remove(user)
        url = '/accounts/' + str(user.userprofile.slug) + '/followers'
        return redirect(url)
    else:
        return redirect(url)


def list_followers(request, slug):
    user_profile = get_object_or_404(UserProfile, slug=slug)
    followers = user_profile.followers.all()
    return render(request, 'followers.html', {'user_profile': user_profile, 'followers': followers})


def list_following(request, slug):
    user = get_object_or_404(UserProfile, slug=slug)
    following = user.following.all()
    return render(request, 'following.html', {'user': user, 'following': following})


def settings(request):
    if request.method == 'POST':
        user = request.user
        fn = request.POST['fn']
        ln = request.POST['ln']
        email = request.POST['email']
        bio = request.POST['bio']
        accent1 = request.POST['accent1']
        accent2 = request.POST['accent2']
        user_profile = user.userprofile
        user.first_name = fn
        user.last_name = ln
        user.email = email
        user.save(update_fields=['first_name', 'last_name', 'email'])
        user_profile.bio = bio
        user_profile.accent1 = accent1
        user_profile.accent2 = accent2
        user_profile.save(update_fields=['bio', 'accent1', 'accent2'])
        url = '/accounts/' + str(user.userprofile.slug)
        return redirect(url)
    else:
        return render(request, 'settings.html')


