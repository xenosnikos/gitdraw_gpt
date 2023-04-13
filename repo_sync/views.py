from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Repository
from .form import RepositoryForm
from .utils import sync_repository, generate_architectural_diagrams

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully.')
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'repo_sync/register.html', {'form': form})

@login_required
def dashboard(request):
    repositories = Repository.objects.filter(user=request.user)
    return render(request, 'repo_sync/dashboard.html', {'repositories': repositories})

@login_required
def add_repository(request):
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        if form.is_valid():
            repo = form.save(commit=False)
            repo.user = request.user
            repo.save()
            messages.success(request, 'Repository added successfully.')
            return redirect('dashboard')
    else:
        form = RepositoryForm()

    return render(request, 'repo_sync/add_repository.html', {'form': form})

@login_required
def sync_repo(request, repo_id):
    repo = Repository.objects.get(pk=repo_id, user=request.user)
    sync_repository(request.user.username, repo.url, repo.name)
    messages.success(request, 'Repository synced successfully.')
    return redirect('dashboard')

@login_required
def generate_diagram(request, repo_id):
    repo = Repository.objects.get(pk=repo_id, user=request.user)
    prompt = "Generate an architectural diagram for this Python project:"
    diagram = generate_architectural_diagrams(request.user.username, repo.name, prompt)
    return render(request, 'repo_sync/diagram.html', {'diagram': diagram, 'repo': repo})

