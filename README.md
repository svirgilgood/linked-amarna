# Amarna Personal Names

This project is looking at ways of analyzing and visualizing the Amarna
Letters.

 
Tools and results from parsing Shlomo Izreel's transcriptions of the Amarna
Letters. [Izreel's transcriptions can be found
here](https://www.tau.ac.il/humanities/semitic/amarna.html). 



## Process for Data Collection and Curation

Order of Scripts:

1. [name_greper.py]('scripts/name_greper.py'). This script downloads the text
   from Shlomo Izreel's website, or uses a text file stored locally. It then
prepares and generates the basic table for the database, as well as creates an
Excel file that can be imported into OpenRefine. The columns might need to be
adjusted in the Excel file to make them easier to work with.
2. OpenRefine (Running Comparisons until diminishing returns are reached). I
   ran the cluster key collision, cluster levenshtein, cluster levenshtein
with the radius updated to 2, and the the cluster levenshetein with block 5.
I should have ran the cluster key collsion in the `name_greper.py` script, as
the OpenRefine cluster key collision is not as good as can be created in
python. The following normalization function is much superior to the one found
in OpenRefine. 
```
import unicodedata 

...

def remove_diacritics(string):
    for c in unicodedeata.normalize('NFD', string):
        if unicodedata.category(c)[0] != 'M':
            yield c 

...
''.join(remove_diacritics(SOMESTRING)
```
After the names have been clustered in OpenRefine, export the file as csv. The
current version of the OpenRefine cluster is saved as
[AmarnaNames4.csv]('data/AmarnaNames4.csv').
3. [name_database_generator.py]('scripts/name_database_generator.py'). This
   function imports yaml file that I created from looking at the index
of Moran's translation of the Amarna Letters, and Hess's Amarna personal
names. [The yaml file is in the data directory]('data/WPACV.yml'). This file
also imports the csv file created from OpenRefine.
4. [name_comparer.py]('scripts/name_comparer.py') and
   [name_insert.py]('scripts/name_insert.py') are used to improve the
database. The name_comparer finds additional clusters that might belong
together, these are updated with the name insert script. Additonal information
is added with the name insert script (like references to Hess's _Amarna
Personal Names_). 
5. [d3_data_generator.py]('scripts/d3_data_generator.py'). This script
   generates the data used for the d3 visualization. The JSON file that is
output from this script should be adjusted so each of the top level keys become
variables, and the file needs to be renamed to `graph4.js`. This was for the
purpose of making the file easier to import into the html page.


## The Webpage 

The resulting data visualization uses a [d3 force directed
graph](https://github.com/d3/d3-force). Also [fusejs](https://fusejs.io/) is
imported to allow for fuzzy searching of the names. 
