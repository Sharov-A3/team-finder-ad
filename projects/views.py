from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProjectForm
from .models import Project

# Константы
ITEMS_PER_PAGE = 12


def paginate_queryset(request, queryset, items_per_page=ITEMS_PER_PAGE):
    """Утилита для пагинации"""
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get("page", 1)
    return paginator.get_page(page_number)


def project_list_view(request):
    projects = Project.objects.select_related("owner").all()
    page_obj = paginate_queryset(request, projects)
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
        },
    )


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"), pk=project_id
    )
    is_owner = request.user.is_authenticated and request.user == project.owner
    is_participant = (
        request.user.is_authenticated and project.participants.filter(pk=request.user.pk).exists()
    )
    is_favorited = (
        request.user.is_authenticated and request.user.saved_projects.filter(pk=project.pk).exists()
    )

    return render(
        request,
        "projects/project-details.html",
        {
            "project": project,
            "is_owner": is_owner,
            "is_participant": is_participant,
            "is_favorited": is_favorited,
        },
    )


@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm()
    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return redirect("projects:detail", project_id=project.id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": True,
        },
    )


@login_required
def complete_project_view(request, project_id):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Method not allowed"},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )

    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Forbidden"}, status=HTTPStatus.FORBIDDEN
        )

    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Already closed"}, status=HTTPStatus.BAD_REQUEST
        )

    project.status = Project.STATUS_CLOSED
    project.save()
    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
def toggle_participate_view(request, project_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    project = get_object_or_404(Project, pk=project_id)
    is_participant = project.participants.filter(pk=request.user.pk).exists()

    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({"status": "ok", "participating": not is_participant})


@login_required
def toggle_favorite_view(request, project_id):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    project = get_object_or_404(Project, pk=project_id)
    is_favorited = request.user.saved_projects.filter(pk=project.pk).exists()

    if is_favorited:
        request.user.saved_projects.remove(project)
    else:
        request.user.saved_projects.add(project)

    return JsonResponse({"status": "ok", "favorited": not is_favorited})


@login_required
def favorite_projects_view(request):
    projects = request.user.saved_projects.select_related("owner").all()
    page_obj = paginate_queryset(request, projects)
    return render(
        request,
        "projects/favorite_projects.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
        },
    )
