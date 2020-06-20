# Hybrid DHash and PHash Framework
This repository houses the implementation of the hybrid dHash and pHash framework. This framework has dHash as the filter and pHash as the main algorithm. 

To run any file in this repository, certain libraries needed to be installed first. For installing them, you can run this command:

```bash
pip3 install -r requirements.txt
```

To run the hybrid framework for FAR testing with sample "images" folder, you can run the following command:
```bash
python3 dhash_and_phash_far.py images/
```
To run the hybrid framework for FRR and ANHD testing with sample "modified\_images" folder, you can run the following command:
```bash
python3 dhash_and_phash_frr_anhd.py modified_images/
```

The dhash\_phash\_ahash\_far.py file contains the functions of dHash, pHash and aHash for FAR testing. You can run the following command for testing the frameworks on sample "images" folder by:
```bash
python3 dhash_phash_ahash_far.py [Framework name] images/
```
For the Framework name, write either dhash, phash or ahash.

The dhash\_phash\_frr\_anhd.py file contains the functions of dHash, pHash, and aHash for FRR and ANHD testing. You can run the following command for testing the frameworks on sample "modified\_images" folder by:
```bash
python3 dhash_phash_frr_anhd.py [Framework name] modified_images/ 
```

For the framework name, write either dhash, phash or ahash.

For testing the blockhash for FAR testing on sample "images" folder, you can run the following command:
```bash
python3 blockhash_far.py images/
```

For testing the Blockhash for FRR and ANHD testing on sample "modified\_images" folder, you can run the following command:
```bash
python3 blockhash_frr_anhd.py modified_images/
```

The original Caltech dataset can be downloaded from [here](http://www.vision.caltech.edu/Image_Datasets/Caltech101/101_ObjectCategories.tar.gz).

To make the datasets to be used in FAR, you can run the following command inside the "101\_ObjectCategories" folder:
```bash
python3 caltech_folder_merger.py images/
```
Now make a folder named "modified\_images" then with the "images" folder you made while making dataset for FAR, we can make the dataset for FRR and ANHD.
```bash
python3 caltech_image_separator.py images/
```


