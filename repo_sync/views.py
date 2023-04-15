from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
#from .utils import create_dot_file_from_analysis
import os
from .models import Repository, File
from .form import RepositoryForm
from .utils import sync_repository,sync_all_repositories
import graphviz
import openai
from dotenv import load_dotenv
import requests

load_dotenv()

openai.api_key = os.environ.get('OPENAI_API_KEY')

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
    sync_all_repositories()
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
    messages.success(request, 'Repository synced successfully.')
    return redirect('dashboard')

def read_files_in_repository(repo_path):
    file_paths = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_paths.append(os.path.join(root, file))

    return file_paths

def analyze_files_with_gpt(file_paths):
    analyzed_files = []

    for file_path in file_paths:
        print(file_path)
        with open(file_path, "r") as f:
            content = f.read()

        prompt = f"Analyze the following code file:\n\n{content}\n\nAnalysis:"

        # Send request to OpenAI API for analysis
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )

        # Print response for debugging
        print(response)

        # Extract analysis from the response
        analysis = response.choices[0].text.strip()

        # Print analysis for debugging
        print(analysis)

        # Append the analysis to the list
        analyzed_files.append({"file_path": file_path, "analysis": analysis})

    return analyzed_files

def create_dot_file_from_analysis(analysis, output_file='diagram.dot'):
    dot = graphviz.Digraph(comment='Repository Diagram')

    # Custom parsing logic for GPT-3.5 output
    for item in analysis:
        element_type = item['type']
        element_name = item['name']
        element_related = item.get('related', [])

        if element_type == 'class':
            if element_name.endswith('Page'):
                dot.node(element_name, shape='box', style='filled', fillcolor='lightblue')
            else:
                dot.node(element_name, shape='box')

        if element_type == 'function':
            dot.node(element_name, shape='ellipse')

        for related_item in element_related:
            related_name = related_item['name']
            related_type = related_item['type']

            if related_type == 'function':
                dot.node(related_name, shape='ellipse')
                dot.edge(element_name, related_name)

            if related_type == 'attribute':
                if 'component' in related_item:
                    component_name = related_item['component']
                    dot.node(component_name, shape='diamond', style='filled', fillcolor='lightgray')
                    dot.node(related_name, shape='ellipse')
                    dot.edge(component_name, related_name)
                elif 'route' in related_item:
                    route_name = related_item['route']
                    dot.node(route_name, shape='box', style='filled', fillcolor='lightgreen')
                    dot.edge(element_name, route_name)
                else:
                    dot.node(related_name, shape='box')
                    dot.edge(element_name, related_name)

    # Save the DOT file
    dot.render(output_file, view=False)

@login_required

def generate_diagram(request):
    # Get all repositories for the current user
    repositories = Repository.objects.filter(user=request.user)


    # Get all files for all synced repositories
    files = File.objects.filter(repository__in=repositories)

    # Analyze the files with GPT-3.5 and generate the analysis
    analysis = analyze_files_with_gpt(files)
    dot_data = create_dot_file_from_analysis(analysis)

    return render(request, 'repo_sync/diagram.html', {'dot_data': dot_data})


