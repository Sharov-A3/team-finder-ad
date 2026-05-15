from http import HTTPStatus

from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from .models import User

# Константы для пагинации
ITEMS_PER_PAGE = 12

# Константы фильтров
FILTER_FAV_AUTHORS = "owners-of-favorite-projects"
FILTER_PARTICIPATED_AUTHORS = "owners-of-participating-projects"
FILTER_LIKE_MINE = "interested-in-my-projects"
FILTER_MY_PARTICIPANTS = "participants-of-my-projects"


def paginate_queryset(request, queryset, items_per_page=ITEMS_PER_PAGE):
    """Утилита для пагинации"""
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page', 1)
    return paginator.get_page(page_number)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('projects:list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('projects:list')
            else:
                form.add_error(None, 'Неверный имейл или пароль')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('projects:list')


def user_detail_view(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/user-details.html', {'user': profile_user})


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user, current_user=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:detail', user_id=request.user.id)
    else:
        form = EditProfileForm(instance=request.user, current_user=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            return redirect('users:detail', user_id=request.user.id)
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


def participants_view(request):
    users_list = User.objects.filter(is_active=True).order_by('id')
    active_filter = request.GET.get('filter')

    if active_filter and request.user.is_authenticated:
        if active_filter == FILTER_FAV_AUTHORS:
            # Авторы избранных проектов
            fav_ids = request.user.saved_projects.values_list('id', flat=True)
            users_list = users_list.filter(owned_projects__id__in=fav_ids).distinct()
        elif active_filter == FILTER_PARTICIPATED_AUTHORS:
            # Авторы проектов, в которых я участвую
            participated_ids = request.user.participated_projects.values_list('id', flat=True)
            users_list = users_list.filter(owned_projects__id__in=participated_ids).distinct()
        elif active_filter == FILTER_LIKE_MINE:
            # Пользователи, которым нравятся мои проекты
            my_project_ids = request.user.owned_projects.values_list('id', flat=True)
            users_list = users_list.filter(saved_projects__id__in=my_project_ids).distinct()
        elif active_filter == FILTER_MY_PARTICIPANTS:
            # Участники моих проектов
            my_project_ids = request.user.owned_projects.values_list('id', flat=True)
            users_list = users_list.filter(participated_projects__id__in=my_project_ids).distinct()

    page_obj = paginate_queryset(request, users_list)

    return render(request, 'users/participants.html', {
        'participants': page_obj,
        'page_obj': page_obj,
        'active_filter': active_filter,
    })