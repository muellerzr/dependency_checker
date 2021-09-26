
# Dependency Checker
> A lightweight pythonic way to verify if python packages are on the latest version


## Install

`pip install dependency-checker`

## How to use

```
from dependency_checker import get_installed_dependencies, check_new_version
```

`dependency_checker` has two functionalities:
- Checking a python project's dependencies
- Checking if a python package is on the latest version

Each are intuitive to use, and have detailed documentation available.

To check a package's dependencies, we can use the `get_installed_dependencies` function, passing in the string name of the module:

```
get_installed_dependencies('dependency-checker', depth_limit=1)
```




    {'dependency-checker': '0.0.1',
     'packaging': '21.0',
     'pip': '21.2.4',
     'pipdeptree': '2.1.0'}



Generally a depth of 1 is enough to get a package's main dependencies, bar `pip`, `packaging`, and other "standard" python resources.

There also exists `check_new_version`, which will see if a package version is the latest available on `pypi`:

```
check_new_version('pipdeptree', '2.0.9')
```




    True


