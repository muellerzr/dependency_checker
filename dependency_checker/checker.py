__all__ = ['get_installed_dependencies', 'is_latest_version']

import json, ast, pipdeptree, sys, subprocess

def get_installed_dependencies(package_name:str, depth_limit:int=1, include_self:bool=False):
    """Recursively grabs dependencies of python package

    Parameters
    ----------
    package_name : str
      The name of a python package
    depth_limit : int
      How deep to follow nested dependencies
    include_self : bool
      Whether to include the original library in the results

    Returns
    -------
    dict
      A dictionary of {package:version}
    """
    pkgs = pipdeptree.get_installed_distributions(local_only=False, user_only=False)
    tree = pipdeptree.PackageDAG.from_pkgs(pkgs)
    tree = tree.filter([package_name], None)
    curr_depth = 0

    def _get_deps(j, dep_dict={}, curr_depth=0):
        if (curr_depth > depth_limit):
            return dep_dict
        if isinstance(j, list):
            for a in j:
                _get_deps(a, dep_dict, curr_depth)
        elif isinstance(j, dict):
            if ('package_name' in j.keys()):
                if (j['package_name'] not in dep_dict.keys()):
                    dep_dict[j['package_name']] = j['installed_version']
            if ('dependencies' in j.keys()):
                curr_depth += 1
                return _get_deps(j['dependencies'], dep_dict, curr_depth)
        return dep_dict
    deps = _get_deps(ast.literal_eval(pipdeptree.render_json_tree(tree, 4)), {})
    if (not include_self):
        deps.pop(package_name, None)
    return deps

def is_latest_version(package_name:str, current_version:str):
    """Compares the current version with the latest version, and returns if they are different

    Parameters
    ----------
    package_name : str
      The name of a pip python package
    current_version : str
      The installed version of a package, such as "1.2.3"

    Returns
    -------
    bool
      Whether the versions are the same
    """
    latest_version = str(subprocess.run([sys.executable, '-m', 'pip', 'install', '{}==random'.format(package_name)], capture_output=True, text=True))
    latest_version = latest_version[(latest_version.find('(from versions:') + 15):]
    latest_version = latest_version[:latest_version.find(')')]
    latest_version = latest_version.replace(' ', '').split(',')[(- 1)]
    if (latest_version == current_version):
        return True
    else:
        return False

