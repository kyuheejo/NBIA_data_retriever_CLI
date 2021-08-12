import tensorflow_datasets as tfds
import pandas as pd
from os import listdir
from os.path import isfile, join
import os
from PIL import Image
from shutil import move
from functools import partial
import numpy as np
import argparse

# The downloaded raw file paths are different from those in description csv in two ways. 
# 1) The filepath is different. There is one extra intermediate folder with data. 
# 2) The filename is different. The file should be of the form "00000.dcm"
# This script is written in order to restructure the file paths as written in the description csv. 

def build_ddsm(args):
    # First, create a dataframe that contains all file paths listed in descritpion csv. 
    df_paths = listdir(args.csv_path)
    df_list = []
    for p in df_paths:
        df = pd.read_csv(join(args.csv_path, p))
        df_list.append(df)
    df = pd.concat(df_list)

    if not args.resume:
        # restructure file paths 
        print("Start restructuring file paths")
        for i in range(len(df)):
            remove_intermediate(df.iloc[i]["image file path"], args.rootdir)
            remove_intermediate(df.iloc[i]["cropped image file path"], args.rootdir)
            remove_intermediate(df.iloc[i]["ROI mask file path"], args.rootdir)
      
        print("Pausing operation. Please convert DICOM files to PNG files and resume by setting --resume flag to True.")

    else: 
        print("Resuming operation. Start renaming files.")

        # rename image files 
        for i in range(len(df)):
            path = df.iloc[i]["image file path"]
            path_list = path.split("/")
            files = listdir(join(args.rootdir, "/".join(path_list[:-1])))
            assert(path_list[-1] == "000000.dcm")
            assert(len(files)==2)
           
            for file in files:
                new_name = "000000" + file[-4:]
                move(join(args.rootdir, "/".join(path_list[:-1]), file), join(args.rootdir, "/".join(path_list[:-1]), new_name))
                print(new_name)
                assert(file[-3:]=="png" or file[-3:]=="dcm")
        
        # rename ROI mask and cropped image files
        find_crop = partial(find, func=np.argmin)
        find_mask = partial(find, func=np.argmax) 

        for i in range(len(df)):
            crop_path = df.iloc[i]["cropped image file path"].replace("\n", "")
            crop_path_list = crop_path.split("/")
            crop_dcm_name = crop_path_list[-1]
            crop_png_name = crop_dcm_name.replace("dcm", "png")
            
            mask_path = df.iloc[i]["ROI mask file path"].replace("\n", "")
            mask_path_list = mask_path.split("/")
            mask_dcm_name = mask_path_list[-1]
            mask_png_name = mask_dcm_name.replace("dcm", "png")
            
            path_to_crop = join(args.rootdir, "/".join(crop_path_list[:-1]))
            crop_png_orig_name = find_crop(path_to_crop)
            crop_dcm_orig_name = crop_png_orig_name.replace("png", "dcm")
            
            move(join(path_to_crop, crop_png_orig_name), join(path_to_crop, crop_png_name))
            move(join(path_to_crop, crop_dcm_orig_name), join(path_to_crop, crop_dcm_name))
            
            path_to_mask = join(args.rootdir, "/".join(mask_path_list[:-1]))
            mask_png_orig_name = find_mask(path_to_mask)
            mask_dcm_orig_name = mask_png_orig_name.replace("png", "dcm")
            
            move(join(path_to_mask, mask_png_orig_name), join(path_to_mask, mask_png_name))
            move(join(path_to_mask, mask_dcm_orig_name), join(path_to_mask, mask_dcm_name))
        
        print("Start building path level DDSM dataset. You can then use tfds to access to the data. ")

        # build dataset
        builder = tfds.builder("curated_breast_imaging_ddsm", data_dir = args.rootdir)
        config = tfds.download.DownloadConfig(extract_dir=args.rootdir, manual_dir=args.rootdir)
        builder.download_and_prepare(download_dir = args.rootdir, download_config = config)


def remove_intermediate(path, rootdir):
    path_list = path.split("/")
    if not isdir(join(rootdir, "/".join(path_list[:-2]))):
        print(f'file path {path} does not exist')
        return
    date = listdir(join(rootdir, "/".join(path_list[:-2])))
    if len(date) == 1 and date[0] != path_list[-2]:
        for file in listdir(join(rootdir, "/".join(path_list[:-2]), *date)):
            move(join(rootdir, "/".join(path_list[:-2]), *date, file), join(rootdir, "/".join(path_list[:-2]), file))      
        os.rmdir(join(rootdir, "/".join(path_list[:-2]), *date))

def find(path, func): 
    files = listdir(path)
    files = [f for f in files if f[-3:]=="png"]
    assert(len(files) == 1 or len(files) == 2)
    if len(files) == 1:
        return files[0]
    else: 
        x, y = [], []
        for f in files:
            img = Image.open(join(path, f))
            x.append(img.size[0])
            y.append(img.size[1])
        assert(func(x) == func(y))
        return files[func(x)]

def bool_flag(s):
    """
    Parse boolean arguments from the command line.
    """
    FALSY_STRINGS = {"off", "false", "0"}
    TRUTHY_STRINGS = {"on", "true", "1"}
    if s.lower() in FALSY_STRINGS:
        return False
    elif s.lower() in TRUTHY_STRINGS:
        return True
    else:
        raise argparse.ArgumentTypeError("invalid value for a boolean flag")

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Cleaning and building ddsm dataset')
    parser.add_argument('--csv_path', default='DDSM', type=str, help='path where 4 description csv files are saved the specified path must only contain the csv files')
    parser.add_argument('--rootdir', default='NBIA_data_retriever_CLI/output/CBIS-DDSM', type=str,
                help="root directory in which DDSM images are saved")
    parser.add_argument('--resume', default=False, type=bool_flag, help='set resume to True after converting DICOM image to png')
    args = parser.parse_args()
    build_ddsm(args)
