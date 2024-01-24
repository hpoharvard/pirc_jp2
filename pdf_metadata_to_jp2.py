## This script is about adding PDF metadata to a jp2 image file

from pdf2image import convert_from_path
import pdf2image
from PIL import Image
from jpylyzer import jpylyzer
import logging
import time, os
import exiftoll

EXIFTOOL_PATH = r'C:\Program Files\exiftool\exiftool(-k).exe'

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
                    print (i.split('.pdf')[0])
                    #reader = PdfReader(z)
                    infofoo = pdf2image.pdfinfo_from_path(z)
                    add_metadata_to_jp2(output_folder, i.split('.pdf')[0], infofoo)
                   
                    #logger_description.info('File Name: ' + str(i) + " - PDF Metadata: " + str(reader.metadata).replace("'",'').replace('{','').replace('}','').replace('/','') + " - PDF Version: " + str(reader.pdf_header)) 
                except Exception as inst:
                    #logger_description.info('File Name: ' + str(i) + " - No able to covert to jp2000")
                    print(type(inst))    # the exception type
                    print(inst.args)     # arguments stored in .args
                    print(inst)

# check if the jp2 are valid jpeg2000 images
def delete_original_jp2(output_folder):
    print (output_folder)
    ext1 = ('jp2_original')
    ext2 = ('jp2')
    dir_list = os.listdir(output_folder)
    logger_validation.info('Check if the jp2 files are valid: ')
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
            except:
                logger_validation.info('File Name: ' + str(files) + " - No able to convert it to jp2000")            


if __name__ == "__main__":
        
    # Replace 'output_folder' with the desired output folder path
    output_folder = r'C:\gis\p2023\jp2\output'
    
    #convert_pdf_to_jp2(pdf_path, output_folder)
    folder_path = r'C:\gis\p2023\jp2\pdf_original'
    
    crawl_finder(folder_path)    
    delete_original_jp2(output_folder)