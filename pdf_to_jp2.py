## This script is about converting the 

from pdf2image import convert_from_path
from PIL import Image
from jpylyzer import jpylyzer
import logging
import time, os
from pypdf import PdfReader

timestr = time.strftime("%Y-%m%d")


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

setup_logger('log_validation', r"C:\\temp\\log_validation.txt")
setup_logger('log_description', r"C:\\temp\\log_description.txt")

logger_validation = logging.getLogger('log_validation')
logger_description = logging.getLogger('log_description')


#def convert_pdf_to_jp2(pdf_path, output_folder):

def convert_pdf_to_jp2(pdf_path, output_folder, filename):
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    print(images)
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save each image as JP2 format
    for i, image in enumerate(images):    
        print (i)
        jp2_path = os.path.join(output_folder, f'p_{filename}.jp2')
           
        ###jp2_path = os.path.join(output_folder, f'page_{i + 1}.jp2')
        #image.save(jp2_path, format='jp2', quality_mode='dB', quality_layers=[80])
        image.save(jp2_path, quality_mode='dB', quality_layers=[100], plt=True)

# check if the jp2 are valid jpeg2000 images
def listoutputfile(output_folder):
    print (output_folder)
    dir_list = os.listdir(output_folder)
    logger_validation.info('Check if the jp2 files are valid: ')
    for i in dir_list:

        z = output_folder + '/' + i
        try:
            # Analyse with jpylyzer, result to Element object
            myResult = jpylyzer.checkOneFile(z)
            status=myResult.findtext('isValid')
            print (status)
            logger_validation.info('File Name: ' + str(i) + " - Status: " + status)
        except:
            logger_validation.info('File Name: ' + str(i) + " - No able to convert it to jp2000")
# inspect folder and subfolders and process all the files
def crawl_finder(path_crawl):
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
                    #print (z)
                    convert_pdf_to_jp2(z, output_folder,i.split('.pdf')[0])
                    reader = PdfReader(z)
                    #print(str(reader.metadata))
                    #print(str(reader.pdf_header))
                    logger_description.info('File Name: ' + str(i) + " - PDF Metadata: " + str(reader.metadata).replace("'",'').replace('{','').replace('}','').replace('/','') + " - PDF Version: " + str(reader.pdf_header)) 
                except:
                    logger_description.info('File Name: ' + str(i) + " - No able to covert to jp2000")
if __name__ == "__main__":
        
    # Replace 'output_folder' with the desired output folder path
    output_folder = r'C:\gis\p2023\jp2\output'
    
    #convert_pdf_to_jp2(pdf_path, output_folder)
    folder_path = r'C:\gis\p2023\jp2\pdf'
    
    crawl_finder(folder_path)    
    listoutputfile(output_folder)