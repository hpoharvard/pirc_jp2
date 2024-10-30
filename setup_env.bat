@echo off
:: Set environment name and required libraries
set ENV_NAME=ENV_NAME
:: Create the conda environment
call C:\ProgramData\Miniconda3\Scripts\conda.exe create -n %ENV_NAME% python=3.9 -y

:: Activate the environment
call C:\ProgramData\Miniconda3\Scripts\activate.bat %ENV_NAME%

:: Optional: Install additional packages with pip if not available via Conda
:: Uncomment the line below if needed
:: pip install package_name

pip install PyExifTool
pip install jpylyzer
pip install pypdf
pip install PyQt5
pip install pdf2image
pip install pillow

:: conda remove --name ENVIRONMENT --all
echo Environment %ENV_NAME% created and packages installed successfully.
pause