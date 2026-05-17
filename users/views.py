from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from users.forms import RegistrationFormUser, LoginFormUser, EditFormUser, ChangePasswordFormUser
from users.models import Skill
from constants import constants_teamfinder as t_constant
import json

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('projects:list')
    if request.method == 'POST':
        form = RegistrationFormUser(request.POST)

        if form.is_valid():
            user = form.save()
            
            login(request, user)

            return redirect('projects:list')
    else:
        form = RegistrationFormUser()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('projects:list')
    
    if request.method == 'POST':
        form = LoginFormUser(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('projects:list')
            else:
                form.add_error(None, 'Неверный email или пароль')
    else:
        form = LoginFormUser()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('projects:list')


def user_detail_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    return render(request, 'users/user-details.html', {'user': user})


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditFormUser(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            return redirect('users:detail', user_id=request.user.pk)
    else:
        form = EditFormUser(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordFormUser(request.user, request.POST)
        
        if form.is_valid():
            form.save()
            login(request, request.user)
            return redirect(USERS_DETAIL_URL, user_id=request.user.pk)
    else:
        form = ChangePasswordFormUser(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


def users_list_view(request):
    users = User.objects.filter(is_active=True)

    active_skill = request.GET.get('skill', '')

    if active_skill:
        users = users.filter(skills__name=active_skill).distinct()
    
    all_skills = Skill.objects.all().order_by('name')
    
    paginator = Paginator(users, t_constant.ITEMS_ON_PAGE)
    
    page_number = request.GET.get('page', t_constant.DEFAULT_PAGE)
    
    page_obj = paginator.get_page(page_number)
    
    context = {
        'participants': page_obj,
        'all_skills': all_skills,
        'active_skill': active_skill,
    }
    
    return render(request, 'users/participants.html', context)


@require_GET
def skills_autocomplete(request):
    query = request.GET.get('q', '')
    
    if query:
        skills = Skill.objects.filter(
            name__istartswith=query
        ).order_by('name')[:t_constant.SKILLS_AUTOCOMPLETE_LIMIT]
    else:
        skills = Skill.objects.none()
    
    skills_data = []
    for skill in skills:
        skills_data.append({
            'id': skill.id,
            'name': skill.name
        })
    
    return JsonResponse(skills_data, safe=False)


@login_required
@require_POST
def skills_add(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if user != request.user:
        return JsonResponse(
            {'error': 'Нельзя редактировать чужой профиль'},
            status=403
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Неверный формат данных'},
            status=400
        )
    
    skill_id = data.get('skill_id')
    name = data.get('name')

    created = False
    added = False
    
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
        
        if not user.skills.filter(pk=skill.pk).exists():
            user.skills.add(skill)
            added = True
    
    elif name:
        skill, created = Skill.objects.get_or_create(name=name.strip())
        
        if not user.skills.filter(pk=skill.pk).exists():
            user.skills.add(skill)
            added = True
    
    else:
        return JsonResponse(
            {'error': 'Нужно указать skill_id или name'},
            status=400
        )
    
    return JsonResponse({
        'skill_id': skill.id,
        'created': created,
        'added': added
    })


@login_required
@require_POST
def skills_remove(request, user_id, skill_id):
    user = get_object_or_404(User, pk=user_id)

    if user != request.user:
        return JsonResponse(
            {'error': 'Нельзя редактировать чужой профиль'},
            status=403
        )

    skill = get_object_or_404(Skill, pk=skill_id)
    
    if user.skills.filter(pk=skill.pk).exists():
        user.skills.remove(skill)
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse(
            {'error': 'У пользователя нет такого навыка'},
            status=400
        )
