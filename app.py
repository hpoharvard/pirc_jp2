import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel
from pdf2image import convert_from_path
import pdf2image
from PIL import Image
from jpylyzer import jpylyzer
import logging
import time, os
from pypdf import PdfReader
import pypdf
import exiftoll
import subprocess
import shutil

EXIFTOOL_PATH = r'C:\\Program Files\\exiftool\\exiftool(-k).exe'
GROK_COMPRESS_PATH = r'C:/Program Files/grok12/bin/grk_compress.exe'

logger_pdf = logging.getLogger('log_pdf')


class FolderSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.folder_path1 = None
        self.folder_path2 = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Folder Selector App')
        self.setGeometry(150, 150, 500, 350)

        self.label1 = QLabel('Input Folder:')
        self.label2 = QLabel('Output Folder:')
        self.label3 = QLabel('Click the button below to start the process!')
        self.label4 = QLabel('')

        self.button_select_folder1 = QPushButton('Select Folder Input', self)
        self.button_select_folder1.clicked.connect(self.select_folder1)

        self.button_select_folder2 = QPushButton('Select Folder Output', self)
        self.button_select_folder2.clicked.connect(self.select_folder2)

        self.button_run_function = QPushButton('PDF to JP2 Conversion', self)
        self.button_run_function.clicked.connect(self.run_function)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.button_select_folder1)
        layout.addWidget(self.label2)
        layout.addWidget(self.button_select_folder2)
        layout.addWidget(self.label3)
        layout.addWidget(self.button_run_function)
        layout.addWidget(self.label4)

        self.setLayout(layout)

    def select_folder1(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder Input')
        if folder_path:
            self.folder_path1 = folder_path
            self.label1.setText(f'Folder Input: {self.folder_path1}')
            self.label1.setStyleSheet("background-color: lightyellow; font-weight: bold; border: 1px solid black;")

    def select_folder2(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder Output')
        if folder_path:
            self.folder_path2 = folder_path
            self.label2.setText(f'Folder Output: {self.folder_path2}')
            self.label2.setStyleSheet("background-color: lightyellow; font-weight: bold; border: 1px solid black;")

    def run_function(self):
        if self.folder_path1 and self.folder_path2:
            setup_logger('log_pdf', os.path.join(self.folder_path2, "log_pdf.txt"))
            logger_pdf.info(f'Start time: {time.strftime("%Y%m%d-%H%M%S")}')
            self.label4.setText('Processing...')
            self.label4.setStyleSheet("background-color: lightblue; font-weight: bold; border: 1px solid black;")

            try:
                crawl_finder(self.folder_path1, self.folder_path2)
                crawl_finder_tiff(self.folder_path2)
                self.label4.setText('Process finished!')
                self.label4.setStyleSheet("background-color: lightgreen; font-weight: bold; border: 1px solid black;")
            except Exception as e:
                self.label4.setText(f'Error: {str(e)}')
                self.label4.setStyleSheet("background-color: red; font-weight: bold; border: 1px solid black;")
                logger_pdf.error(f'Error during processing: {str(e)}')

            logger_pdf.info(f'End time: {time.strftime("%Y%m%d-%H%M%S")}')
        else:
            self.label4.setText('Please select both folders before running the function.')
            self.label4.setStyleSheet("background-color: yellow; font-weight: bold; border: 1px solid black;")


def convert_pdf_to_tiff(pdf_path: str, output_folder: str, filename: str) -> str:
    images = convert_from_path(pdf_path, dpi=300)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    tiff_path = ""
    for i, image in enumerate(images):
        try:
            filename_new = filename.replace('.', '_')
            tiff_path = os.path.join(output_folder, f'{filename_new}.tiff')
            image.save(tiff_path, dpi=(300, 300))
        except Exception as e:
            logger_pdf.error(f'PDF File Name: {filename} - Unable to convert to TIFF. Error: {str(e)}')
    return tiff_path


def convert_tiff_to_jp2(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        logger_pdf.error(f"Input file '{input_path}' not found.")
        return

    command = [
        GROK_COMPRESS_PATH,
        '-i', input_path,
        '-o', output_path,
        '-p', 'RLCP',
        '-t', '1024,1024',
        '-EPH',
        '-SOP'
    ]
    try:
        subprocess.run(command, check=True)
        logger_pdf.info(f"Conversion successful. JPEG 2000 image saved at '{output_path}'.")
    except subprocess.CalledProcessError as e:
        logger_pdf.error(f"Conversion failed. Error: {e}")

#def crawl_finder(path_crawl, output_folder):
def crawl_finder(path_crawl: str, output_folder: str) -> None:
    pdf_count = 0
    valid_jp2 = 0
    # Walk through the folder and its subfolders
    for root, _, files in os.walk(path_crawl):
        # Count the PDF files in the current directory
        pdf_count += sum(1 for file in files if file.lower().endswith('.pdf'))    
       
    logger_pdf.info(f'Number of PDF files to process: {pdf_count}')
    logger_pdf.info('Convert PDF files to JP2: ')
    logger_pdf.info('')

    for root, _, file_names in os.walk(path_crawl):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            if os.path.isdir(file_path):
                continue
            if file_name.lower().endswith('.pdf'):
                try:
                    infofoo = pdf2image.pdfinfo_from_path(file_path)
                    reader = PdfReader(file_path)
                    totalpages = len(reader.pages)

                    if totalpages > 1:
                        logger_pdf.info(f'File Name: {file_name} - Multipage PDF. No JP2 conversion.')
                    else:
                        try:
                            tiff_path = convert_pdf_to_tiff(file_path, output_folder, file_name.split('.pdf')[0])
                            jp2_path = os.path.join(output_folder, f"{file_name.split('.pdf')[0]}.jp2")
                            convert_tiff_to_jp2(tiff_path, jp2_path)
                            os.remove(tiff_path)
                            # Analyse with jpylyzer, result to Element object
                            myResult = jpylyzer.checkOneFile(jp2_path)
                            status = myResult.findtext('isValid')
                            print (status)
                            if status:                             
                                valid_jp2 += 1
                                move_jp2_to_original_folder(jp2_path, root)
                            logger_pdf.info(f'File Name: {file_name} - JP2 conversion completed.')
                        except Exception as e:
                            logger_pdf.error(f'File Name: {file_name} - Unable to convert to JP2. Error: {str(e)}')
                        try:
                            add_metadata_to_jp2(jp2_path, infofoo)
                        except Exception as e:
                            logger_pdf.error(f'File Name: {file_name} - Unable to add metadata. Error: {str(e)}')

                except Exception as e:
                    logger_pdf.error(f'File Name: {file_name} - Error during processing. Error: {str(e)}')
    logger_pdf.info('')
    logger_pdf.info(f'Number of valid JP2 moved to origin: {valid_jp2} ')    

def add_metadata_to_jp2(jp2_path: str, infofoo: dict) -> None:
    metadata_commands = []

    title = f'-Title={infofoo.get("Title", "NA") or "NA"}'
    creator = f'-Creator={infofoo.get("Creator", "NA") or "NA"}'
    author = f'-Author={infofoo.get("Author", "NA") or "NA"}'
    producer = f'-Producer={infofoo.get("Producer", "NA") or "NA"}'
    pdf_version = f'-PDFVersion={infofoo.get("PDF version", "NA") or "NA"}'

    metadata_commands.extend([title, creator, author, producer, pdf_version])

    with exiftoll.exiftool.ExifTool(EXIFTOOL_PATH) as et:
        for command in metadata_commands:
            et.execute(bytes(command.encode()), bytes(jp2_path.encode()))


def delete_original_tiff(output_folder: str) -> None:
    ext1 = 'tiff_original'
    for file_name in os.listdir(output_folder):
        file_path = os.path.join(output_folder, file_name)
        try:
            if file_name.endswith(ext1):
                os.remove(file_path)
        except Exception as e:
            logger_pdf.error(f'File Name: {file_name} - Error during validation. Error: {str(e)}')


def move_jp2_to_original_folder(jp2_file: str, original_folder: str) -> None:
    if os.path.exists(jp2_file):
        shutil.move(jp2_file, original_folder)
        logger_pdf.info(f'Moved JP2 file {jp2_file} back to {original_folder}')
    else:
        logger_pdf.error(f'JP2 file {jp2_file} not found in {os.path.dirname(jp2_file)}')


def setup_logger(logger_name: str, log_file: str, level=logging.INFO) -> None:
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        formatter = logging.Formatter('%(message)s')
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.setLevel(level)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)


def crawl_finder_tiff(path_crawl: str) -> None:
    for root, _, file_names in os.walk(path_crawl):
        for file_name in file_names:
            if file_name.lower().endswith('.tiff'):
                file_path = os.path.join(root, file_name)
                if os.path.isdir(file_path):
                    continue
                try:
                    jp2_path = os.path.join(root, f"{os.path.splitext(file_name)[0]}.jp2")
                    convert_tiff_to_jp2(file_path, jp2_path)
                    os.remove(file_path)
                    move_jp2_to_original_folder(jp2_path, root)
                except Exception as e:
                    logger_pdf.error(f'File Name: {file_name} - Unable to convert to JP2. Error: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FolderSelectorApp()
    window.show()
    sys.exit(app.exec_())
