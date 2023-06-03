# Sistema de Información Ambiental (SIA)

**Version:** 1.1.0

GUI Application to facilitate the download, exploration and visual analysis of oceanographic data.

Page of the project: https://sia-information-system.github.io/sia-website

## Table of contents

- [Install](#install)
  - [Requirements before installation](#requirements-before-installation)
  - [Production mode](#production-mode)
  - [Development mode](#development-mode)
- [Usage](#usage)
- [Documentation](#documentation)
- [Contributions](#contributions)

## Install

### Requirements before installation

This package depends indirectlys on [Cartopy](https://scitools.org.uk/cartopy/docs/latest/) v0.21.1,
which is a package that in order to be installed by `pip` needs to have some C/C++ libraries available in
the host operating system, which it's not a problem in Linux or MacOS, but it is on Windows.
See the [Cartopy installation docs](https://scitools.org.uk/cartopy/docs/latest/installing.html)
to see how to install required dependencies on Linux and MacOS.

If you are on Windows, in order to simplify the installation of this package, we recommend to
use the pre-built Cartopy binaries distributed by `conda` (`anaconda`/`miniconda`). Once you have
`conda`, you can install Cartopy with the following command:

``` bash
conda install cartopy=0.21.1
```

Before install this package make sure you have the C/C++ library installed
on your operating system to build Cartopy, or have the pre-built binaries
installed on the environment you are going to use.

### Production mode

You can install this package from PyPI using:

``` bash
pip install sia-app
```

To install the package from source code, clone the repo from GitHub and
run the following command in the package root directory 
(where the `pyproject.toml` file is located):

``` bash
pip install .
```

See [local installation](https://pip.pypa.io/en/stable/topics/local-project-installs/) for details.

### Development mode

**NOTE**: For development it's recommended to use an isolated environment.
You can use tools like `anaconda` / `minionda` or `virtualenv` to create
this kind of environments. On Windows, due to the reasons exposed in the
[Requirements before installation](#requirements-before-installation) section,
we highly recommend to use `conda` as environments manager. If you are on
other operating systen, you don't use conda and you decide to store the
environment in the root directory of the project, name the environment as
`venv` since this name of directory is ignored by git.

To install the package in development mode (--editable), run the following command
in the package root directory (where de `pyproject.toml` file is located):

``` sh
pip install --editable .[dev]
```

See [local installation](https://pip.pypa.io/en/stable/topics/local-project-installs/) for details.


This application depends on two packages to extract data and create charts. These packages
are:

- [siaextractlib](https://github.com/sia-information-system/siaextractlib)
- [siaplotlib](https://github.com/sia-information-system/siaplotlib)

Fundamental features regarding to these topics (data extraction and chart building)
are added first in those packages and then are used here.

To increase the version number, the package `bumpver` is used.
[Read the docs](https://github.com/mbarkhau/bumpver#reference)
to see how to use it.

## Usage

You can start the app by running the following command:

``` bash
sia-app
```

Aditionally, you can start the app in debug mode by running:

``` bash
sia-app-debug
```

This will log all the messages to the stderr output.

## Documentation

You can see some video tutorials (in spanish) about how to use this application
[here](https://sia-information-system.github.io/sia-website/pages/tutorials.html).

Docs about the code will be added later.

## Contributions

Rules are:

- First ask to maintainers if the new proposed feature can be added. You can open an issue on GitHub.
- Document every new feature added.
