import subprocess
import time, os
from jpylyzer import jpylyzer
import logging

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

setup_logger('log_tif_validation', r"C:\\temp\\log_tif_validation.txt")
setup_logger('log_tif_description', r"C:\\temp\\log_tif_description.txt")

logger_tif_validation = logging.getLogger('log_tif_validation')
logger_tif_description = logging.getLogger('log_tif_description')

def convert_tiff_to_jp2(input_path, output_path):
    # Check if the input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    # Run the grokj2k command for conversion
    command = [
        r'C:/gis/p2023/jp2/grok/bin/grk_compress.exe',
        '-i', input_path,
        '-o', output_path,
        '--irreversible',  # Enable lossless compression
        '-p RLCP -t 1024,1024 -EPH -SOP -I -q 42'
    ]

    try:        
        subprocess.run(command, check=True)
        print(f"Conversion successful. JPEG 2000 image saved at '{output_path}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Conversion failed. {e}")

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
                    out = output_folder + "\\" + i.split('.')[0] + ".jp2"
                    print (z,out)
                    convert_tiff_to_jp2(z, out)                    
                    logger_tif_description.info('File Name: ' + str(i)) 
                except:
                    logger_tif_description.info('File Name: ' + str(i) + " - No able to covert to jp2000")
                    print('error')


# check if the jp2 are valid jpeg2000 images
def listoutputfile(output_folder):
    print (output_folder)
    dir_list = os.listdir(output_folder)
    #logger_validation.info('Check if the jp2 files are valid: ')
    for i in dir_list:

        z = output_folder + '/' + i
        try:
            # Analyse with jpylyzer, result to Element object
            myResult = jpylyzer.checkOneFile(z)
            status=myResult.findtext('isValid')
            print (status)
            logger_tif_validation.info('File Name: ' + str(i) + " - Status: " + status)
        except:
            logger_tif_validation.info('File Name: ' + str(i) + " - No able to convert it to jp2000")
            print("error")        

if __name__ == "__main__":

    # Example usage
    #input_tiff_path = r'C:\gis\p2023\jp2\ca.tif'
    #output_jpeg2000_path = r'C:\gis\p2023\jp2\output\tif\output_image_test_3.jp2'

    output_folder = r'C:\gis\p2023\jp2\output\tif'
    path_crawl = r'C:\gis\p2023\jp2\tif'

    #convert_tiff_to_jpeg2000(input_tiff_path, output_jpeg2000_path)
    crawl_finder(path_crawl)
    listoutputfile(output_folder)