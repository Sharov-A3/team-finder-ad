from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import User
from .forms import RegisterForm, LoginForm, EditProfileForm, ChangePasswordForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/projects/list/')
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
                return redirect('/projects/list/')
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
    
    # Фильтры для варианта 1
    active_filter = request.GET.get('filter')
    if active_filter and request.user.is_authenticated:
        if active_filter == 'owners-of-favorite-projects':
            fav_ids = request.user.favorites.values_list('id', flat=True)
            users_list = users_list.filter(owned_projects__id__in=fav_ids).distinct()
        elif active_filter == 'owners-of-participating-projects':
            participated_ids = request.user.participated_projects.values_list('id', flat=True)
            users_list = users_list.filter(owned_projects__id__in=participated_ids).distinct()
        elif active_filter == 'interested-in-my-projects':
            my_project_ids = request.user.owned_projects.values_list('id', flat=True)
            users_list = users_list.filter(favorites__id__in=my_project_ids).distinct()
        elif active_filter == 'participants-of-my-projects':
            my_project_ids = request.user.owned_projects.values_list('id', flat=True)
            users_list = users_list.filter(participated_projects__id__in=my_project_ids).distinct()
    
    paginator = Paginator(users_list, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/participants.html', {
        'participants': page_obj,
        'page_obj': page_obj,
        'active_filter': active_filter,
    })