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

logger_pdf = logging.getLogger('log_pdf')

#Image.MAX_IMAGE_PIXELS=None

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
            self.label1.setText(f'Folder Input : {self.folder_path1}')
            self.label1.setStyleSheet("background-color: lightyellow; font-weight: bold; border: 1px solid black;") 

    def select_folder2(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder Output')
        if folder_path:
            self.folder_path2 = folder_path
            self.label2.setText(f'Folder Output: {self.folder_path2}')
            self.label2.setStyleSheet("background-color: lightyellow; font-weight: bold; border: 1px solid black;") 

    def run_function(self):
        if self.folder_path1 and self.folder_path2:
            setup_logger('log_pdf', self.folder_path2 + r"\\log_pdf.txt")
            logger_pdf.info('Start time: ' + str(time.strftime("%Y%m%d-%H%M%S")))
            
            # Replace this function with your custom logic to run
            print(f'Running function with Folder Input: {self.folder_path1} and Folder Output: {self.folder_path2}')
            crawl_finder(self.folder_path1, self.folder_path2)
            crawl_finder_tiff(self.folder_path2)
            listoutputfile(self.folder_path2, self.folder_path1)           
            self.label4.setText('Process finished!')
            # setting up background color 
            self.label4.setStyleSheet("background-color: lightgreen; font-weight: bold; border: 1px solid black;")
            logger_pdf.info('End time: ' + str(time.strftime("%Y%m%d-%H%M%S")))
        else:
            print('Please select both folders before running the function.')

def convert_pdf_to_jp2(pdf_path, output_folder, filename, commentinfo):
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300)
    #print(images)
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save each image as JP2 format
    for i, image in enumerate(images):
        try:    
            #print (filename)
            #print (commentinfo)            
            filename_new = filename.replace('.', '_')
            #print (filename, filename_new)            
            jp2_path = os.path.join(output_folder, f'{filename_new}.tiff')
            ###jp2_path = os.path.join(output_folder, f'page_{i + 1}.jp2')
            #image.save(jp2_path, format='jp2', quality_mode='dB', quality_layers=[80])
            #image.MAX_IMAGE_PIXELS = None
            #image.save(jp2_path, quality_mode='dB', quality_layers=[100], plt=True)
            image.save(jp2_path, dpi=(300,300)) 
        except Exception as inst:                
                logger_pdf.info('PDF File Name: ' + str(i) + " - No able to convert it to jp2.")
                #print(type(inst))    # the exception type
                #print(inst.args)     # arguments stored in .args
                #print(inst)

# inspect folder and subfolders and process all the files
def crawl_finder(path_crawl, output_folder):
    # List all files in the folder
    files = os.listdir(path_crawl)
    # Count the PDF files
    pdf_count = str(sum(1 for file in files if file.lower().endswith('.pdf')))
    logger_pdf.info('Number of PDF files to process: ' + pdf_count)
    logger_pdf.info('Convert PDF files to jp2: ')
    for root, dir_names, file_names in os.walk(path_crawl):
        #print (root)
        dir_list = os.listdir(root)
        for i in dir_list:
            #print (i.split('.pdf')[0])
            z = root + '\\' + i            
            if (os.path.isdir(z)):
                continue
            else:
                try:                    
                    infofoo = pdf2image.pdfinfo_from_path(z)
                    #print(infofoo)
                    reader = PdfReader(z)
                    totalpages = len(reader.pages)
                    if (totalpages > 1):
                        #print ("Log the name of the multipage pdf and skip the conversion")
                        logger_pdf.info('File Name: ' + str(i) + " - Multipage PDF. No jp2 conversion.")                   
                    else:
                        #print(totalpages, z)
                        try:
                            convert_pdf_to_jp2(z, output_folder,i.split('.pdf')[0],infofoo)
                            logger_pdf.info('File Name: ' + str(i) + " - jp2 conversion completed.")                                                         
                        except Exception as inst:
                            logger_pdf.info('File Name: ' + str(i) + " - No able to covert to jp2000")
                            #print(type(inst))    # the exception type
                            #print(inst.args)     # arguments stored in .args
                            #print(inst)
                        try:
                            add_metadata_to_jp2(output_folder, i.split('.pdf')[0], infofoo)                            
                        except Exception as inst:
                            logger_pdf.info('File Name: ' + str(i) + " - No able to covert to jp2000")
                            #print(type(inst))    # the exception type
                            #print(inst.args)     # arguments stored in .args
                            #print(inst)
                        try:                            
                            delete_original_jp2(output_folder)
                        except Exception as inst:
                            logger_pdf.info('File Name: ' + str(i) + " - No able to covert to jp2000")
                            #print(type(inst))    # the exception type
                            #print(inst.args)     # arguments stored in .args
                            #print(inst)
                    
                    #
                    #print(str(reader.metadata))
                    #print(str(reader.pdf_header))
                    #logger_description.info('File Name: ' + str(i) + " - PDF Metadata: " + str(reader.metadata).replace("'",'').replace('{','').replace('}','').replace('/','') + " - PDF Version: " + str(reader.pdf_header)) 
                except:
                    print('')
                    #logger_description.info('File Name: ' + str(i) + " - No able to covert to jp2000")
    #listoutputfile(output_folder)

def add_metadata_to_jp2(output_folder, filepdf, infofoo):
    # Convert PDF to images
    #ext = ('jp2')
    ext = ('tiff')
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # iterating over all files
    for files in os.listdir(output_folder):
        if files.endswith(ext):            
            #if(files.split('.jp2')[0] == filepdf):
            
            if(files.split('.tiff')[0] == filepdf.replace('.', '_')):
                fileno = output_folder + "\\"+ files
                # get the Title
                if(dict(infofoo).get('Title') is None):                                       
                    title = '-Title = NA'                    
                    #print (title)
                else:                     
                    if(infofoo['Title'] == ''):
                        title = '-Title = NA'                   
                        #print(title)
                    else:
                        title = '-Title = ' + infofoo['Title']                    
                        #print(title)
                # get the Creator
                if(dict(infofoo).get('Creator') is None):                          
                    creator = '-Creator = NA'
                    #print (creator)
                else:
                    if(infofoo['Creator'] == ''):
                        creator = '-Creator = NA'
                    else:    
                        creator = '-Creator = ' + infofoo['Creator']
                        #print(creator)
                # get the Author
                if(dict(infofoo).get('Author') is None):                          
                    author = '-Author = NA'
                    #print (author)
                else:
                    if(infofoo['Author'] == ''):
                        author = '-Author = NA'
                    else:    
                        author = '-Author =' + infofoo['Author']
                        #print(author)
                # get the Producer
                if(dict(infofoo).get('Producer') is None):                          
                    producer = '-Producer = NA'
                    #print (producer)
                else:
                    if(infofoo['Producer'] == ''):
                        producer = '-Producer = NA'
                    else:
                        producer = '-Producer = ' + infofoo['Producer']
                    #print(producer)
                # get the PDF version 
                if(dict(infofoo).get('PDF version') is None):                          
                    pdfVersion = '-PDFVersion = NA'
                    #print (pdfVersion)
                else:
                    if(infofoo['PDF version'] == ''):
                        pdfVersion = '-PDFVersion = NA'
                    else:    
                        pdfVersion = '-PDFVersion = ' + infofoo['PDF version']
                        #print(pdfVersion)   

                with exiftoll.exiftool.ExifTool(EXIFTOOL_PATH) as et:                
                    et.execute(bytes(title.encode()),bytes(fileno.encode())) # title
                    et.execute(bytes(creator.encode()),bytes(fileno.encode())) # creator
                    et.execute(bytes(author.encode()),bytes(fileno.encode())) # author
                    et.execute(bytes(producer.encode()),bytes(fileno.encode())) # producer
                    et.execute(bytes(pdfVersion.encode()),bytes(fileno.encode())) # pdfVersion                    
        else:
            continue    

# check if the jp2 are valid jpeg2000 images
def delete_original_jp2(output_folder):
    #print (output_folder)
    ext1 = ('tiff_original')
    ext2 = ('jp2')
    dir_list = os.listdir(output_folder)    
    for files in os.listdir(output_folder):
            z = output_folder + '/' + files        
            try:
                # Analyse with jpylyzer, result to Element object
                if files.endswith(ext1):
                    #print(files)
                    os.remove(z)
                elif files.endswith(ext2):
                    myResult = jpylyzer.checkOneFile(z)
                    status=myResult.findtext('isValid')
                    #print (status)
                    #logger_validation.info('File Name: ' + str(i) + " - Status: " + status)
                else:
                    continue
            except Exception as inst:
                #logger_validation.info('File Name: ' + str(files) + " - No able to convert it to jp2000")
                #print(type(inst))    # the exception type
                print(inst.args)     # arguments stored in .args
                #print(inst)            

# check if the jp2 are valid jpeg2000 images
def listoutputfile(output_folder, destination_folder):
    valid_jp2 = 0
    #print (output_folder)    
    dir_list = os.listdir(output_folder)
    logger_pdf.info('Check if the jp2 files are valid: ')
    ext2 = ('.jp2')
    for i in dir_list:        
        z = output_folder + '/' + i
        #print(z)
        if i.endswith(ext2):
            try:
                # Analyse with jpylyzer, result to Element object
                myResult = jpylyzer.checkOneFile(z)
                status = myResult.findtext('isValid')                
                #print (status)
                logger_pdf.info('File Name: ' + str(i) + " - Status: " + status)
                valid_jp2 += 1
                src_path = os.path.join(output_folder, i)
                dst_path = os.path.join(destination_folder, i)
                shutil.move(src_path, dst_path)
            except:
                logger_pdf.info('File Name: ' + str(i) + " - No able to convert it to jp2000")
        else:
            continue
    logger_pdf.info('Number of valid JP2 moved to origin: ' + str(valid_jp2))
# loggers
def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)

def convert_tiff_to_jp2(input_path, output_path):
    # Check if the input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    # Run the grokj2k command for conversion    
    command = [
        r'C:/Program Files/grok12/bin/grk_compress.exe',
        '-i', input_path,
        '-o', output_path,  
        '-p RLCP',
        '-t 1024,1024',
        '-EPH',
        '-SOP'
    ]
    try:        
        subprocess.run(command, check=True)
        print(f"Conversion successful. JPEG 2000 image saved at '{output_path}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Conversion failed. {e}")    

# inspect folder and subfolders and process all the files
def crawl_finder_tiff(path_crawl):
    for root, dir_names, file_names in os.walk(path_crawl):
        #print (root)
        dir_list = os.listdir(root)
        for i in dir_list:
            if(i.endswith('.tiff')):
                #print (i.split('.pdf')[0])                
                z = root + '\\' + i
                #print(z)
                if (os.path.isdir(z)):
                    continue
                else:
                    try:
                        out = path_crawl + "\\" + i.split('.')[0] + ".jp2"
                        #print (z,out)
                        convert_tiff_to_jp2(z, out)
                        os.remove(z)                    
                        #logger_tif_description.info('File Name: ' + str(i)) 
                    except:
                        #logger_tif_description.info('File Name: ' + str(i) + " - No able to covert to jp2000")
                        print('error')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FolderSelectorApp()
    window.show()
    sys.exit(app.exec_())