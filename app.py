import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel
from pdf2image import convert_from_path
import pdf2image
from PIL import Image
from jpylyzer import jpylyzer
import logging
import time, os
from pypdf2 import PdfReader
import pypdf2
import exiftoll

EXIFTOOL_PATH = r'C:\Program Files\exiftool\exiftool(-k).exe'

timestr = time.strftime("%Y-%m%d")

Image.MAX_IMAGE_PIXELS=None

class FolderSelectorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.folder_path1 = None
        self.folder_path2 = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Folder Selector App')
        self.setGeometry(350, 300, 400, 250)

        self.label1 = QLabel('Input Folder:')
        self.label2 = QLabel('Output Folder:')
        self.label3 = QLabel('Click the button below to start the process!')
        self.label4 = QLabel('')
        

        self.button_select_folder1 = QPushButton('Select Folder Input', self)
        self.button_select_folder1.clicked.connect(self.select_folder1)

        self.button_select_folder2 = QPushButton('Select Folder Output', self)
        self.button_select_folder2.clicked.connect(self.select_folder2)

        self.button_run_function = QPushButton('PDF to JP2 Conversation', self)
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
            self.label1.setStyleSheet("background-color: lightyellow; border: 1px solid black;") 

    def select_folder2(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder Output')
        if folder_path:
            self.folder_path2 = folder_path
            self.label2.setText(f'Folder Output: {self.folder_path2}')
            self.label2.setStyleSheet("background-color: lightyellow; border: 1px solid black;") 

    def run_function(self):
        if self.folder_path1 and self.folder_path2:
            # Replace this function with your custom logic to run
            print(f'Running function with Folder Input: {self.folder_path1} and Folder Output: {self.folder_path2}')
            crawl_finder(self.folder_path1, self.folder_path2)           
            self.label4.setText('Process finished!')
            # setting up background color 
            self.label4.setStyleSheet("background-color: lightgreen; font-weight: bold; border: 1px solid black;")            
                       
            
        else:
            print('Please select both folders before running the function.')

def convert_pdf_to_jp2(pdf_path, output_folder, filename, commentinfo):
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300)
    print(images)
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save each image as JP2 format
    for i, image in enumerate(images):    
        #print (i)
        #print (commentinfo)
        jp2_path = os.path.join(output_folder, f'p_{filename}.jp2')
           
        ###jp2_path = os.path.join(output_folder, f'page_{i + 1}.jp2')
        #image.save(jp2_path, format='jp2', quality_mode='dB', quality_layers=[80])
        #image.MAX_IMAGE_PIXELS = None
        image.save(jp2_path, quality_mode='dB', quality_layers=[100], plt=True)

# inspect folder and subfolders and process all the files
def crawl_finder(path_crawl, output_folder):
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
                    print(infofoo)
                    reader = PdfReader(z)
                    totalpages = len(reader.pages)
                    if (totalpages > 1):
                        print ("Log the name of the multipage pdf and skip the conversion")                   
                    else:
                        print(totalpages, z)
                        try:
                            convert_pdf_to_jp2(z, output_folder,i.split('.pdf')[0],infofoo)   
                            add_metadata_to_jp2(output_folder, i.split('.pdf')[0], infofoo)
                            delete_original_jp2(output_folder) 
                        except Exception as inst:
                            #logger_description.info('File Name: ' + str(i) + " - No able to covert to jp2000")
                            print(type(inst))    # the exception type
                            print(inst.args)     # arguments stored in .args
                            print(inst)      
                    
                    #
                    #print(str(reader.metadata))
                    #print(str(reader.pdf_header))
                    #logger_description.info('File Name: ' + str(i) + " - PDF Metadata: " + str(reader.metadata).replace("'",'').replace('{','').replace('}','').replace('/','') + " - PDF Version: " + str(reader.pdf_header)) 
                except:
                    print('')
                    #logger_description.info('File Name: ' + str(i) + " - No able to covert to jp2000")

def add_metadata_to_jp2(output_folder, filepdf, infofoo):
    # Convert PDF to images
    ext = ('jp2')
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # iterating over all files
    for files in os.listdir(output_folder):
        if files.endswith(ext):            
            if(files.split('.jp2')[0].split('p_')[1] == filepdf):
                fileno = output_folder + "\\"+ files
                # get the Title
                if(dict(infofoo).get('Title') is None):                                       
                    title = '-Title = NA'                    
                    print (title)
                else:                     
                    title = '-Title = ' + infofoo['Title']                    
                    print(title)
                # get the Creator
                if(dict(infofoo).get('Creator') is None):                          
                    creator = '-Creator = NA'
                    print (creator)
                else:
                    creator = '-Creator = ' + infofoo['Creator']
                    print(creator)
                # get the Author
                if(dict(infofoo).get('Author') is None):                          
                    author = '-Author = NA'
                    print (author)
                else:
                    author = '-Author =' + infofoo['Author']
                    print(author)
                # get the Producer
                if(dict(infofoo).get('Producer') is None):                          
                    producer = '-Producer = NA'
                    print (producer)
                else:
                    producer = '-Producer = ' + infofoo['Producer']
                    print(producer)
                # get the PDF version 
                if(dict(infofoo).get('PDF version') is None):                          
                    pdfVersion = '-PDFVersion = NA'
                    print (pdfVersion)
                else:
                    pdfVersion = '-PDFVersion = ' + infofoo['PDF version']
                    print(pdfVersion)   

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
    print (output_folder)
    ext1 = ('jp2_original')
    ext2 = ('jp2')
    dir_list = os.listdir(output_folder)    
    for files in os.listdir(output_folder):
            z = output_folder + '/' + files        
            try:
                # Analyse with jpylyzer, result to Element object
                if files.endswith(ext1):
                    print(files)
                    os.remove(z)
                elif files.endswith(ext2):
                    myResult = jpylyzer.checkOneFile(z)
                    status=myResult.findtext('isValid')
                    print (status)
                    #logger_validation.info('File Name: ' + str(i) + " - Status: " + status)
                else:
                    continue
            except Exception as inst:
                #logger_validation.info('File Name: ' + str(files) + " - No able to convert it to jp2000")
                print(type(inst))    # the exception type
                print(inst.args)     # arguments stored in .args
                print(inst)            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FolderSelectorApp()
    window.show()
    sys.exit(app.exec_())