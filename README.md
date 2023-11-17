# Skyscan 3 Python Migration #

## Overview ##

This repository contains the code of the Skyscan project

The target of the project is to obtain warehouse inventory information from photographs of the shelves obtained by means of a Drone.

The program receives as input a set of images of the racks to be inventoried, as well as certain configuration information, and generates:

1. An output text file with the information on the pallets and labels detected in each photograph as well as their position on a map of the shelf.

2. A rack image map composed of all the images positioned according to the information obtained

## Design notes ##

The information is temporarily stored in an internal database that must be initialized before its execution.

Processing is organized by **racks** and an entitity named **inventory_reference** that groups all images of a rack taken in an inventory activity. This allows to store the results of several inventory activities of the same rack in the database.

The process is carried out in the following steps:

1. Detection by means of Machine Lerning algorithms of pallets, labels, and elements of the shelves used for the positioning of the images.

2. Label processing and obtaining of bar codes and texts

3. Calculation of the position of each image and generation of information on pallets and labels per shelf. This activity can be performed in different ways: 
   - by image matching and panoramic reconstruction of the rack image or 
   - by reading the positions from an excel file

4. Generation of ouput files

For the generation of the graphical information, the program uses an image reference that is defined when the rack is initialized in the database. 

The horizontal dimension of this image is the number of rack columns * the number of pixel per column + 2 * a margin in pixels

The vertical dimension of this image is the number of rack rows * the number of pixel per row plus + 2 * a margin in pixels

The number of pixels per row and column and the number of pixels per margin are internal parameters equal to:

"row_height": 3500

"column_width": 4000

"rack_margin": 3500, 

These dimensions have been defined in order to be close to the size of the actual photographs, but note that the size of this image is unmanageable, for this reason everytime an image is to be generated a scale factor to reduce its size must be provided.

### Shelf and position naming ###

The program assumes that the photographs are always taken from left to right. 

The program organizes the pallet positions in **shelves**. Each shelf contains three pallets. The entity **section** indicates the position of the pallet in the shelf and goes from 1 to 3 starting from the left. 

A **column** is a set of shelves arranged vertically in a rack. Columns are numbered from the left starting with 0.

**Rows** refer to the vertical position of the shelves and are numbered from down to top starting with number 0, thus a pallet position is determined by the row, column and section.

In addition to this naming, customers usually have their own mumbering criteria for the pallet columns. This information is stored in a variable named **customer column reference** (customer_col_ref) which, if available, is stored in the output text file.


### Positioning algorithms ###

The program can use several alternative image positioning algorithms.

#### Displacement calculation ####

This algorithm performs the positioning of the images by calculating the displacement between consecutive images and generates a mosaic image that represents the entire rack by overlapping image over image according to the image displacement and the detection of rack references. The result is an image like the following:

![Scheme](Examples/doc_images/rack_image.jpg)

For the use of this algorithm it is essential that the images overlap at least 40% to be able to detect the displacement of one image against the previous one.

### Reading the image position from a predefined file ###

This algorithm assumes that a photograph is taken for each position. No overlapping between the images is needed since the position is assigned according to the information obtained from an excel file.

Photographs can be taken per pallet position or per shelf grouping three pallets in the iamge

The system can read the positions in two ways: 

- A flight map can be provided in which all positions that should be photographed are listed in a sequential order. The positioning is done using a predetermined flight schedule in which all the positions that have to be photographed are specified in a way that each photograph of the folder is assigned to a position consecutively. For example first photograph in the folder is assigned to position specified in the first row of the text file, the second to the position of the second row and so on. If there is exactly one image per position in the file and these are taken in the right order, the results are correct. The user must remove manually duplicated images from the initial directory, and if there are positions that are not photographed, the corresponding lines must be removed from the map file.

- Additionally the program can also read an excel file in which the positions are stated for each photograph. This is the case when a manual positioning has been performed generating a list with the exact position of each image. This is staed in a parameter named read_name_from_excel

In both cases the format of the excel file expected is the same:

 1st column(A) is the rack name used and stored in the DB
 3rd column(C) is the customer column reference
 5th column(E) is the image name used if read_name_from_excel is set to true
 6th column(F) is the column; 
 7th column(G) is the section; this value not needed when scope is "BOX"
 8th column(H) is the rack row used in all cases

An excel file example can bee found in the example folder

## Installation ##

- Clone this directory


```bash

$ git clone git@bitbucket.org:chep-skyscan/chep-skyscan-detection.git

```


- Copy weights, cfg and text detection pb files to config folder. The program requires two weights and two cfg files for pallets, label and rack elements detection and one file for text detection 


```bash

$ cp /path/to/weight/files/yolov4_custom_shelf.cfg /path/to/config
$ cp /path/to/weight/files/yolov4_custom_shelf.weights /path/to/config
$ cp /path/to/weight/files/yolov4_custom_detector.cfg /path/to/config
$ cp /path/to/weight/files/yolov4_custom_detector.weights /path/to/config
$ cp /path/to/weight/files/frozen_east_text_detection.pb /path/to/config

```


- Edit config.py file with the location of the weights files


- Install required packages


```bash

$ pip install -r requirements.txt

```


## Program execution ##

The program is run always from the same script which is **main.py** stating the action that is to be executed and the parameters needed in each step. Action is stated by parameter -a 

In all steps, the rack name must be stated with keyword -r or --rack_name and the inventory ref must be stated with parameter -i or --inventory_ref, for example


```bash

$ python main.py -a detect -r name_of_rack -i inventory_ref -input /path/to/input/folder

```

In all cases the program can be run with display option -d xxx where xxx is the number to milliseconds to display, and it will display the intermediate results in a screen window during that interval of time, this option must not be stated when running in batch or the progrma will crash  

### Detection and tag reading

The first step of the program is the detection of items in the image (pallets, tags and shelf elements) and the reading of the bar codes and texts in the tags. The result of this action is a JSON file per image that contains the results of the detection.

This action can be performed on an image by image basis withe the following command:

```bash

$ python main.py -a detect -r rack_name -i inventory_ref -input /path/to/input/folder -img name_of_image_file -out /path/to/output/folder

```
Alternatively, if the -img parameter is not provided, the program will perfom the detections on all the files in the input folder.

This action requires the following mandatory arguments:
- the alphanumeric identifier of the rack given by keyword --rack_name or -ra
- the alphanumeric identifier of the inventory execution reference given by the keyword -i or --inventory
- the folder where the images are stored given by the keyword -input or --input_path
- the folder where the results will be stored given by the keyword -output or --output_path

The following arguments are not mandatory and if not stated the default option is used

- option "web" indicates that a a web service is to be used if the barcodes are not read programmatically, if not stated the service is not invoked
- option "overlap" indicates that the positioning of the image is performed by overlapping comparison
- option "scope" indicates if the images are focused in one pallet positon or in a whole box. Options for this argument are "BOX" or "SECTION". Default value is section


IMPORTANT: The output files are not stored directly in the output folder but in a subfolder within this named rackname_inventory in order not to mix results of different processes. If there s already a folder with this name and files inside, the program stops. This can be avoided by specifying the parameter -force that will delete the output folder if it existed before the detection process.

```bash

$ python main.py -a detect -r rack_name -i inventory_ref -input /path/to/input/folder -img name_of_image_file -out /path/to/output/folder -force

```

### Database initialization ###

Once the detections have been performed and the results files produced, the program loads this results in an internal database that used to store the intermediate results of the process until the final output is produced. In this phase, the rack entity that stores rack configuration information like number of rows and columns is created, then all the JSON files produced in the detection phase are loaded into the database. 

This action is executed with the following command:

```bash

python main.py -a init_db  -input /path/to/JSON/files -r rack_name -i inventory_ref -sc number_of_shelf_columns -rr number_of_rack_rows

```

First of all, the rack must be created in the database. This action is indicated with the word "init_db".
If this option is selected, the following arguments are mandatory:
- the alphanumeric identifier of the rack given by keyword --rack_name or -ra
- the alphanumeric identifier of the inventory execution reference given by the keyword -i or --inventory
- the number of shelf columns with the keyword --shelf_columns or -sc 
- the number of rack rows with the keyword --rack_rows or -rr
- the pallets per shelf with the keyword --pallets_per_shelf or -ps
- the name of the folder where the results of the detection phase are

NOTE: The name of the input folder is handled the same way as the output of the detection phase, thus the naming must be the same.

For example in order to create a rack entity with identifier 4-P with 7 rows and 40 columns, and load the results of a set of images stored in the folder files/detections, the following command should be run:

```bash

$ python main.py -a init_db -input files/detections -r 4-P --rack_rows 7 -shelf_columns 40

```

In addition to these arguments, if keyword --create_database is entered, the program will create a new database from scratch, this will remove all information in the database

If argument --force or -f is entered, the program will rewrite the rack in the database. This option allows, for example, changing the size in columns or reows of a rack without destroying the existing database.


### Image positioning ###

The program offers several possibilities to perform the image positioning

#### Positioning by image matching ####

 This is performed in 2 steps, first a program is run to detect the isplacement of one image againts the previous one. Images must overlap. 

 These steps require the identifiers of the rack and of the inventory reference

 This is performed with the following command:


```bash

   $ python main.py -a dis -r 4-P -i test22

```


Then in a second step images are positioned on the map 

```bash

   $ python main.py -a pos -r 4-P -i test22

```


#### Positioning by excel file ####

If an excel position file is available, the action is specified by **read_excel**.

This action requires the following parameters:

- the alphanumeric identifier of the rack given by keyword --rack_name or -ra
- the alphanumeric identifier of the inventory execution reference given by the key word -i or --inventory
- the name of the excel file given by the keyword -excel or --excel_file

Additionally if option **read_image** is given, the program will read the image name from the corresponding column

```bash
  
  python main.py -a read_excel -r 202i_Lidl -i 220628 -excel /examples/flight_map/Mapeo_202impar_1palet.xlsx -d 200  

```

### Generation of results ###

Once the detection and postioning processes have been run, the user can request the generation of the results files. A json file with the information of images and detections can be requested with the following command:


```bash

$ python main.py -a json -r 4-P -i 220303 -output /path/to/desired/output/folder

```


If the otuput parameter is not specified, the file will be generated in a folder named output in the same folder where the code is

An image file can be generated with the command draw. In this case it is mandatory to state the scale to reduce the reference image  


```bash

$ python main.py -a draw -r 4-P -i 220303 -output /path/to/desired/output/folder

```


If the otuput parameter is not specified, the file will be generated in a folder named output in the same folder where the code is


# SkyScan Anonymizer #

### What is this repository for? ###

* This script anonymizes image files by detecting faces in them and replacing the image section with a blurred or pixelated image.

* The algorithm uses Caffe Model, a generic detector from the OpenCV library that gives good result


### Installation ###



1. Install required packages

```bash

$ pip install -r requirements.txt

```

### How do I get set up? ###

anon_images.py is a python file that must be executed giving as a parameter the files folder where the images are located or the name of one image file

&NewLine;
&NewLine;
```bash

$ python anon_images.py -f "/path/to/images"

```

Accepts the following optional parameters:

* -over (overwrite): if included, the modified images are stored with the same name as the initials, thereby losing information from the original images

* -out (output folder): if included, the modified images are stored in a folder with the given name, if the folder does not exist, the program will try to create it

* -i (interactive): run interactively showing the process

* -m (method): anonymization method, options are "simple" or "pixelated" by default it is the "simple" which is blur, the user can specify the number of pixelated blocks with the -b parameter

&NewLine;
&NewLine;

```bash

$ python anon_images -f "/path/to/images"  -out "path/to/pixelated" -m "pixelated" -b 8

```

Option -c: allows the user to define the minimum confidence level for the face detector


### Thumbnail creator ###

create_thumbnails.py is a program to create thumbnails from an image or set of images

It requires at least the following parameters:

* -f (file or folder name)

* -s (scale) the scale to reduce the images

* -w (width) the width of the reduced images, either the scale or the width must be provided, if both parameters are provided, the width is ignored

* -out (output folder): name of the folder where the thumbnails will be stored, if the folder does not exist, the program will try to create it

* -i (interactive): run interactively showing the process

&NewLine;
&NewLine;
```bash

$ python create_thumbnails.py -f "/path/to/images" -out "path/to/thumbnails" -s 0.2

```

