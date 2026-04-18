from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project


@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, 'projects/list.html', {'projects': projects})


@login_required
def project_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            project = Project.objects.create(user=request.user, name=name, description=description)
            messages.success(request, f'Project "{project.name}" created.')
            return redirect('projects:detail', pk=project.pk)
        messages.error(request, 'Project name is required.')
    return render(request, 'projects/create.html')


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    datasets = project.datasets.all()
    ml_results = project.ml_results.all()
    return render(request, 'projects/detail.html', {
        'project': project,
        'datasets': datasets,
        'ml_results': ml_results,
    })


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            project.name = name
            project.description = description
            project.save()
            messages.success(request, 'Project updated.')
            return redirect('projects:detail', pk=project.pk)
        messages.error(request, 'Project name is required.')
    return render(request, 'projects/edit.html', {'project': project})


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted.')
        return redirect('projects:list')
    return render(request, 'projects/delete.html', {'project': project})
