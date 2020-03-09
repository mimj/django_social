from pprint import pprint

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.decorators.http import require_POST

from accounts.forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm

# CUSTOM LOGIN #
# def user_login(request):
#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(username=cd['username'], password=cd['password'])
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return HttpResponse('Authenticated successfully')
#                 else:
#                     return HttpResponse('Disabled accounts')
#             else:
#                 return HttpResponse("Invalid Login")
#     else:
#         form = LoginForm()
#     return render(request=request, template_name='accounts/login.html', context={'form': form})
from accounts.models import Profile, Contact
from actions.models import Action
from actions.utils import create_action
from common.decorators import ajax_required


@login_required
def dashboard(request):
    # Display all actions by default
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',
                                                       flat=True)
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]

    return render(request,
                  'accounts/dashboard.html',
                  {'section': 'dashboard',
                   'actions': actions})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid():
            new_user = user_form.save(commit=False)

            new_user.set_password(user_form.cleaned_data['password'])

            new_user.save()

            profile = Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
            return render(request=request,
                          template_name='accounts/register_done.html',
                          context={'new_user': new_user})
        else:
            # TODO: This Should be fixed. correctly handle errors
            #  FIX: should show message on template
            for error in user_form.errors:
                pprint(error)
            return HttpResponse(user_form.errors)
    else:
        user_form = UserRegistrationForm()
        return render(request=request, template_name='accounts/register.html', context={'form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')

    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request=request, template_name='accounts/edit.html', context={
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request,
                  'accounts/user/list.html',
                  {'section': 'people',
                   'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User,
                             username=username,
                             is_active=True)
    return render(request,
                  'accounts/user/detail.html',
                  {'section': 'people',
                   'user': user})


@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user,
                                              user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'ko'})
    return JsonResponse({'status': 'ko'})
