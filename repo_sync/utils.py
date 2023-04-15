import os
import git
import openai

from django.conf import settings
from dotenv import load_dotenv
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


def sync_repository(user, repo_url, repo_name):
    repo_directory = get_repo_directory(user, repo_name)

    if os.path.exists(repo_directory):
        pull_repository(user, repo_name)
    else:
        clone_repository(user, repo_url, repo_name)


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
