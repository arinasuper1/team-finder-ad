from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Project
from .forms import ProjectForm
from constants import constants_teamfinder as t_constant

def redirect_to_list(request):
    return redirect('projects:list')


def project_list_view(request):
    projects = Project.objects.all().order_by('-created_at')

    paginator = Paginator(projects, t_constant.ITEMS_ON_PAGE)

    page_number = request.GET.get('page', t_constant.DEFAULT_PAGE)

    page_obj = paginator.get_page(page_number)

    return render(request, 'projects/project_list.html', {'projects': page_obj})


def project_detail_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        
        if form.is_valid():
            project = form.save(commit=False)

            project.owner = request.user

            project.save()

            project.participants.add(request.user)

            return redirect('projects:detail', project_id=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': False
    })


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        
        if form.is_valid():
            form.save()
            return redirect('projects:detail', project_id=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True,
        'project': project
    })


@login_required
@require_POST
def toggle_participate(request, project_id):
    
    project = get_object_or_404(Project, pk=project_id)
    
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participating = False
    else:
        project.participants.add(request.user)
        participating = True
    
    return JsonResponse({
        'status': 'ok',
        'participating': participating
    })


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    if project.owner != request.user:
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Только автор может завершить проект'
            },
            status=403
        )
    
    if project.status != 'open':
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Проект уже завершён'
            },
            status=400
        )
    
    project.status = 'closed'
    project.save()
    
    return JsonResponse({
        'status': 'ok',
        'project_status': 'closed'
    })
