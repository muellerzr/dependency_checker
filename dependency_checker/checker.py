# AUTOGENERATED! DO NOT EDIT! File to edit: 00_checker.ipynb (unless otherwise specified).

__all__ = ['get_installed_dependencies', 'is_latest_version', 'get_github_repo_from_pypi', 'get_latest_release_notes',
           'check_for_newer_release']

# Cell
import json, ast, sys, subprocess

from pipdeptree._discovery import get_installed_distributions
from pipdeptree._models import PackageDAG
from pipdeptree._render import render_json_tree

from github import Github

import requests

from packaging.version import parse
import sys

if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata

# Cell
def get_installed_dependencies(
    package_name:str, # The name of a python package
    depth_limit:int=1, # How deep to follow nested dependencies
    include_self:bool=False, # Whether to include the original library in the results
) -> dict: # A dictionary of {package:version}
    "Recursively grabs dependencies of python package"
    pkgs = get_installed_distributions(local_only=False, user_only=False)
    tree = PackageDAG.from_pkgs(pkgs)
    tree = tree.filter([package_name], None)
    curr_depth=0
    def _get_deps(j, dep_dict={}, curr_depth=0):
        if curr_depth > depth_limit: return dep_dict
        if isinstance(j, list):
            for a in j:
                _get_deps(a, dep_dict, curr_depth)
        elif isinstance(j, dict):
            if 'package_name' in j.keys():
                if j['package_name'] not in dep_dict.keys():
                    dep_dict[j['package_name']] = j['installed_version']
            if 'dependencies' in j.keys():
                curr_depth += 1
                return _get_deps(j['dependencies'], dep_dict, curr_depth)
        return dep_dict
    deps = _get_deps(ast.literal_eval(render_json_tree(tree)), {})
    if not include_self: deps.pop(package_name, None)
    return deps

# Cell
def is_latest_version(
    package_name:str, # The name of a pip python package
    current_version:str, # The installed version of a package, such as "1.2.3"
) -> bool: # Whether the versions are the same
    "Compares the current version with the latest version, and returns if they are different"
    latest_version = str(subprocess.run([sys.executable, '-m', 'pip', 'install', '{}==random'.format(package_name)], capture_output=True, text=True))
    latest_version = latest_version[latest_version.find('(from versions:')+15:]
    latest_version = latest_version[:latest_version.find(')')]
    latest_version = latest_version.replace(' ','').split(',')[-1]

    if latest_version == current_version:
        return True
    else:
        return False

# Cell
def get_github_repo_from_pypi(
    name:str # The name of a pypi package
):
    "Gets the Github URL for a pypi package"
    url = f"https://pypi.org/pypi/{name}/json"
    r = requests.get(url)
    urls = r.json()["info"]["project_urls"]
    for url in urls.values():
        if "github.com" in url:
            return "/".join(url.split("github.com/")[1].split("/")[:2])
    return ""

# Cell
def get_latest_release_notes(
    package:str # The name of a pypi package
):
    "Gets the URL for the latest release notes of a pypi package from Github if available"
    client = Github()
    url = get_github_repo_from_pypi(package)
    if url != "":
        repo = client.get_repo(url)
        try:
            latest = repo.get_latest_release()
            notes_url = latest.html_url
            release_tag = latest.tag_name
            return {"notes_url":notes_url, "release_tag":release_tag}
        except Exception as e:
            if e.args[0] == 404:
                return {}
            raise
    return {}

# Cell
def check_for_newer_release(
    package:str, # The name of a pypi package
    version:str = None # An optional version number
) -> bool:
    "Checks if a newer release is available and then finds the release notes"
    if version is None:
        version = parse(importlib_metadata.version(package))
    if not is_latest_version(package, str(version)):
        notes = get_latest_release_notes(package)
        if notes != {}:
            s = f"Newer version of `{package}` was found available on pypi ({str(version)} -> {notes['release_tag']})\n\n"
            s += f"To upgrade run `pip install {package} -U`\n\n"
            if _in_notebook():
                from IPython.display import display, Markdown
                s += f"[Click Here]({notes['notes_url']}) to see the latest release notes."
                display(Markdown(s))
            else:
                s += f"To read the latest release notes go to: {notes['notes_url']}"
                print(s)
                return True
        else:
            return False
    return False