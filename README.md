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
1. Run 

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
