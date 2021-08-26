# Complete guide to using NBIA data retriever CLI for CBIS-DDSM dataset

Guide to downloading and cleaning CBIS-DDSM dataaset through NBIA data retriever CLI.

---

## Instruction 

### Step 1. Downloading data 

1. git clone 
2. Download ".tcia" manifest file from [this link](https://wiki.cancerimagingarchive.net/display/Public/CBIS-DDSM) and save it in this git repository 
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
<path to dataset> should be like: <path to dataset>/Mass-Training_P_01981_RIGHT_MLO_1/1.3.6.../000000.png. If you followed the instructions above, it should be somthing like: output/CBIS-DDSM
3. Convert DICOM files to PNG files by running the following commands 
```bash
find $DATASET_DCIM_DIR -name '*.dcm' | \
xargs -n1 -P8 -I{} bash -c 'f={}; dcmj2pnm $f | convert - ${f/.dcm/.png}'
```
4. Now run build_ddsm.py once again with --resume flag set to true. This should (1) rename files and (2) build tfds dataset. 
```bash
python build_ddsm.py --csv_path <path to csv files> --rootdir <path to dataset> --resume true
```


### Step 3. Using the built dataset 
 
  Now you can use the final tfds dataset to train and test your model. The dataset contains 224x224 patches extracted from CBIS-DDSM dataset divided into five classes: normal(0), benign_calcification (1), benign_mass (2), malignant_calcification (3), and malignant_mass (4). For more information about the dataset, refer to [this link](https://www.tensorflow.org/datasets/catalog/curated_breast_imaging_ddsm)
  
  For example, he following code snippet creates a pytorch dataset from tfds dataset. 
  ```bash
    # load tfds dataset 
    ds, ds_info = tfds.load('curated_breast_imaging_ddsm',
                    data_dir = <path to dataset>,
                    with_info = True,
                    as_dataset_kwargs={'shuffle_files':False, 'batch_size':-1})
    ds_test    = ds['train'] # either train, test, or validation
    # load data as numpy 
    my_x = tfds.as_numpy(ds_test)['image']
    my_y = tfds.as_numpy(ds_test)['label']
    # transform to torch tensor
    tensor_x = torch.Tensor(my_x) 
    tensor_y = torch.Tensor(my_y)
    # create a pytorch dataset
    dataset = TensorDataset(tensor_x, tensor_y)
  ```
  To learn more about using a tfds dataset please refer to [this link](https://www.tensorflow.org/datasets)
  
