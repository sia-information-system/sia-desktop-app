# Oceanographic and Meteorological Data Extractor and Processor

## Python Packages required

* [Pillow](https://pypi.org/project/Pillow/). Command to install: `pip install Pillow`
* [ttkbootstrap](https://pypi.org/project/ttkbootstrap/). Command to install: `pip install ttkbootstrap`
* [xarray](https://pypi.org/project/xarray/). Command to install: `pip install xarray`
* [netCDF4](https://pypi.org/project/netCDF4/). Command to install: `pip install netCDF4`
* [numpy](https://pypi.org/project/numpy/). Command to install: `pip install numpy`
* [pyinstaller]() 

## How to run app

**NOTE:** You need to first create and fill the `etc/config.ini` file before running the the app. 
See the template `etc/config.ini.example`.

Once done, at the project root directory, run the following command to start the application:

``` sh
python src/main.py
```