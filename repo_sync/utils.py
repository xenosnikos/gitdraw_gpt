import os
import git
import openai
import graphviz
from django.http import request

from .models import Repository,File
from django.conf import settings
from dotenv import load_dotenv
from django.shortcuts import  get_object_or_404

load_dotenv()

def get_repo_directory(user, repo_name):
    return os.path.join(settings.BASE_DIR, f'repositories/{user}/{repo_name}')


def clone_repository(user, repo_url, repo_name):
    repo_directory = get_repo_directory(user, repo_name)

    if not os.path.exists(repo_directory):
        os.makedirs(repo_directory)
        git.Repo.clone_from(repo_url, repo_directory)


def pull_repository(user, repo_name):
    repo_directory = get_repo_directory(user, repo_name)

    if os.path.exists(repo_directory):
        repo = git.Repo(repo_directory)
        repo.remotes.origin.pull()

def sync_repositories(user):
    repositories = Repository.objects.filter(user=user)
    for repository in repositories:
        sync_repository(user.username, repository.url, repository.name)

def sync_repository(repository):
    repo_directory = get_repo_directory(repository.user.username, repository.name)

    if os.path.exists(repo_directory):
        pull_repository(repository.user.username, repository.name)
        for root, dirs, files in os.walk(repo_directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                # Check if the file already exists in the database
                if not File.objects.filter(repository=repository, path=filepath).exists():
                    # Create a File object for the file and associate it with the repository
                    file = File(repository=repository, name=filename, path=filepath)
                    file.save()

    else:
        clone_repository(repository.user.username, repository.url, repository.name)

def sync_all_repositories():
    repositories = Repository.objects.all()
    for repository in repositories:
        sync_repository(repository)

def generate_architectural_diagrams(user, repo_name, prompt):
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    model_engine = "gpt-3.5-turbo"
    repo_directory = get_repo_directory(user, repo_name)
    code_content = ""

    for root, _, files in os.walk(repo_directory):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r') as file_handle:
                    code_content += file_handle.read()

    prompt = f"{prompt} {code_content}"

    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=200,  # Adjust based on the desired response length
        n=1,
        stop=None,
        temperature=0.8,
    )

    return response.choices[0].text.strip()

def create_dot_file_from_analysis(analysis, output_file='diagram.dot'):
    dot = graphviz.Digraph(comment='Repository Diagram')

    # Customize the analysis data parsing depending on the GPT-3.5 output
    for item in analysis:
        element_type = item['type']
        element_name = item['name']
        element_related = item.get('related', [])

        if element_type == 'class':
            dot.node(element_name, shape='record')

        for related_item in element_related:
            related_name = related_item['name']
            related_type = related_item['type']

            if related_type == 'method':
                dot.node(related_name, shape='ellipse')
                dot.edge(element_name, related_name)

            if related_type == 'attribute':
                dot.node(related_name, shape='box')
                dot.edge(element_name, related_name)


    # Send request to OpenAI API for dot generation
    prompt = f"Generate a dot file for the repository diagram:\n\n{dot.source}\n\n"
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=1024,
        temperature=0.5,
        n=1,
        stop=None,
        timeout=60,
    )

    # Extract the dot file from the response
    dot_file = response.choices[0].text.strip()

    # Write the dot file to disk
    with open(output_file, 'w') as f:
        f.write(dot_file)