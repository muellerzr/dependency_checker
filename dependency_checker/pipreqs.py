__all__ = ['extract_project_dependencies', 'generate_requirements_file']

from pipreqs.pipreqs import get_all_imports
from .checker import get_installed_dependencies

from typing import Union, List
from fastcore.basics import merge, listify
from fastcore.script import call_parse, Param
from fastcore.xtras import Path

def extract_project_dependencies(folder_name:Union[(str, Path)], depth_limit:int=1, ignore_dependencies:Union[(str, List[str])]=[], ignore_libraries:Union[(str, List[str])]=[]):
    """Looks at a project folder, and pulls out all dependencies utilized in it

    Parameters
    ----------
    folder_name : Union[(str, Path)]
      Name of a folder containing the source code for a python project
    depth_limit : int
      The maximum recursive depth, when following a dependency's tree
    ignore_dependencies : Union[(str, List[str])]
      Libraries who's dependency versions we ignore and instead use the library version
    ignore_libraries : Union[(str, List[str])]
      List of explicit library names that we remove from the final version dictionary

    Returns
    -------
    dict
      A dictionary of `{package:version}` for a project
    """
    surface_level_deps = get_all_imports(folder_name)
    all_deps = {}
    for dep in surface_level_deps:
        library_deps = get_installed_dependencies(dep, depth_limit=depth_limit, include_self=True)
        for lib in listify(ignore_dependencies):
            if (lib in library_deps.keys()):
                library_deps = {dep: library_deps[dep]}
                break
        all_deps = merge(all_deps, library_deps)
    ignore_libraries = listify(ignore_libraries)
    if (len(ignore_libraries) > 0):
        for lib in ignore_libraries:
            if (lib in all_deps.keys()):
                all_deps.pop(lib)
    return all_deps


@call_parse
def generate_requirements_file(folder_name:Param('Name of a folder containing source code for a python project', str), depth_limit:Param("The maximum recursive depth, when following a dependency's tree", int)=1, ignore_dependencies:Param("Libraries who's dependency versions we ignore and instead use the library version", str)=[], ignore_libraries:Param('List of explicit library names that we remove from the final version dictionary', str)=[], requirements_file_name:Param('Name of requirements file', str)='requirements.txt', new_requirements_path:Param('Relative location to store requirements file', str)='.', override_existing_requirements:Param('Whether to override the requirements file (0/1)', int)=0):
    """Builds a requirements.txt file from a project folder to a directory

    Parameters
    ----------
    folder_name : Param('Name of a folder containing source code for a python project', str)
    depth_limit : Param("The maximum recursive depth, when following a dependency's tree", int)
    ignore_dependencies : Param("Libraries who's dependency versions we ignore and instead use the library version", str)
    ignore_libraries : Param('List of explicit library names that we remove from the final version dictionary', str)
    requirements_file_name : Param('Name of requirements file', str)
    new_requirements_path : Param('Relative location to store requirements file', str)
    override_existing_requirements : Param('Whether to override the requirements file (0/1)', int)
    """
    if (not Path(folder_name).exists()):
        raise ValueError(f'Warning! {folder_name} is not an existing relative path to a folder!')
    project_deps = extract_project_dependencies(folder_name, depth_limit, ignore_dependencies, ignore_libraries)
    dep_strings = []
    for (dep, version) in project_deps.items():
        dep_strings.append(f'{dep}=={version}')
    new_requirements_path = Path(new_requirements_path)
    if (not new_requirements_path.exists()):
        new_requirements_path.mkdir(parents=True)
    requirements_file_path = (Path(new_requirements_path) / requirements_file_name)
    if (requirements_file_path.exists() and (not override_existing_requirements)):
        raise ValueError(f'Warning! {requirements_file_name} already exists, and `override_existing_requirements` is set to False')
    else:
        requirements_file_path.touch()
        requirements_file_path.write_text('\n'.join(dep_strings))

