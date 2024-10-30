@echo off
:: Set environment name and required libraries
set ENV_NAME=pdf2jp2_test
set REQUIRED_LIBS="pypdf pyqt pdf2image pillow"  :: Add your required libraries here
set REQUIRED_LIBS_PIP="PyExifTool jpylyzer"
:: Create the conda environment
call C:\ProgramData\Miniconda3\Scripts\conda.exe create -n %ENV_NAME% python=3.9 -y

:: Activate the environment
call C:\ProgramData\Miniconda3\Scripts\activate.bat %ENV_NAME%

:: Install required libraries
call C:\ProgramData\Miniconda3\Scripts\conda.exe install %REQUIRED_LIBS% -y

call C:\ProgramData\Miniconda3\Scripts\pip.exe install %REQUIRED_LIBS_PIP% -y
:: Optional: Install additional packages with pip if not available via Conda
:: Uncomment the line below if needed
:: pip install package_name
:: conda remove --name ENVIRONMENT --all
echo Environment %ENV_NAME% created and packages installed successfully.
pause