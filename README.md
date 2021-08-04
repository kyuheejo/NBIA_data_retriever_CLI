# NBIA data retriever CLI

Guide to downloading and cleaning CBIS-DDSM dataaset through NBIA data retriever CLI.

---

## Command line usage

### Step 1. Downloading data 

1. git clone 
2. Download ".tcia" manifest file from [this link](https://wiki.cancerimagingarchive.net/display/Public/CBIS-DDSM) and save it in this directory 
3. Use following commands to download CBIS-DDSM under output/ folder

```bash
mkdir output
docker build --tag nbia . 
docker run -v ${PWD}/output:/output nbia -i cbis-ddsm.tcia -o /output -p 8 -t 1200000 
```

### Step 2. Cleaning and building dataset 
Once the dataset is downloaded, you'll notice that the downloaded raw file paths are different from those specified in description csv in two ways. 
1) Paths to files are different. It contains one extra intermediate folder (date).
2) File names are different. File names should be of the form "000000.dcm," not arbitrarily long numbers as it is. 
Furthermore, we ought to convert DICOM files to PNG files for the purpose of training. 

In order to clean the dataset to match description csv files, follow these steps:
1. Download all description csv files from [this link](https://wiki.cancerimagingarchive.net/display/Public/CBIS-DDSM) and save all of them to a separate folder (caution: that specific folder should contain all FOUR description csv files, and description csv file ONLY)
2. Run build_ddsm.py with --resume flag set to false (default). This should remove intermediate directories. 
```bash
python build_ddsm.py --csv_path <path to csv files> --rootdir <path to dataset> --resume false
```
<path to dataset> should be like: <path to dataset>/Mass-Training_P_01981_RIGHT_MLO_1/1.3.6.../000000.png. If you followed the instructions above, it should be somthing like: NBIA_data_retriever_CLI/output/CBIS-DDSM
3. Convert DICOM files to PNG files by running the following commands 
```bash
find $DATASET_DCIM_DIR -name '*.dcm' | \
xargs -n1 -P8 -I{} bash -c 'f={}; dcmj2pnm $f | convert - ${f/.dcm/.png}'
```
4. Now run build_ddsm.py once again with --resume flag set to true. This should (1) rename files and (2) build tfds dataset. For more information about the resulting tfds dataset, refer to [this link](https://www.tensorflow.org/datasets/catalog/curated_breast_imaging_ddsm)
```bash
python build_ddsm.py --csv_path <path to csv files> --rootdir <path to dataset> --resume true
```


---

### [Update 2020.12.24]

Add `--username` and `--passwd`, maybe this is usedful retrive the restriced data.

>> I do not have an account for  NBIA, therefore, this is no tested yet.

---

### [Update 2019.09.17]

Just noticed original NBIA add tar wrapper of real dcm files

Now I add a tar wrapper to decompress the dcm files.
At the same time, I cannot check the download progress of single file anymore.
Therefore, I use a json file to record information of single seriesUID, and mark the relevant file of the seriesUID has been downloaded.

---

Issues with NBIA data retriever:

- Cannot resume download, if there is any error occurs, have to download all files from the beginning
- Swing is kind of heavy, and cannot run it in server

---
Advantages:

- Proxy like `socks5://127.0.0.1:1080` or `http://127.0.0.1:1080`
- Resume download
- Command line

---

Known issues:

- The `public.cancerimagingarchive.net/nbia-download/servlet` use `POST` to transfer data from server to local
, the connection may be terminated even before the download is complete. Therefore, **PLEASE** set timeout as huge as possible
- progress bar is a mess when using multiple process
- I do not have a account of NBIA, therefore this program could not handle the restricted data for now.
