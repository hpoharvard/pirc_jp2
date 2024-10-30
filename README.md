# PIRC convert PDF file to jp2
Those are pyhton scripts to convert PDF and TIF to jp2
1. pdf_to_jp2.py -- script to convert a PDF file to jp2
2. tif_to_jp2.py -- script to convert a TIF file to jp2
3. pdf_metadata_to_jp2.py -- script to add PDF metadata to jp2
4. app.py -- script to create jp2 format from PDF files
5. app.bat -- bat file to call app.py

Besides the python libraries there are two software requirements:
1. exiftoll - https://exiftool.org/
2. grok12 - https://github.com/GrokImageCompression/grok/releases

Install process:
1. Install Python CONDA (https://www.anaconda.com/)
2. Download and install the exiftool tool (https://exiftool.org/)
3. Copy the folder "production" from R drive (R:\GIS\Client\PIRC\2024\pdf2jp2) to your C drive or download this git repo.
4. Run the batch file setup_env.bat (make sure the minicoda3 paths are correct)
5. Modify the files app.bat and app.py from the folder "production" to match your conda path