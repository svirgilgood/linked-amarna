# Amarna Personal Names

This project is looking at ways of analyzing and visualizing the Amarna
Letters.

 
Tools and results from parsing Shlomo Izreel's transcriptions of the Amarna
Letters. [Izreel's transcriptions can be found
here](https://www.tau.ac.il/humanities/semitic/amarna.html). 


[Linked Amarna](site/index.html)


## Process for Data Collection and Curation

Order of Scripts:
1. [name_greper.py](https://github.com/e2dubba/linked-amarna/blob/master/scripts/name_greper.py). This script downloads the text
   from Shlomo Izreel's website, or uses a text file stored locally. It then
prepares and generates the basic table for the database, as well as creates an
Excel file that can be imported into OpenRefine. The columns might need to be
adjusted in the Excel file to make them easier to work with.
2. [OpenRefine](https://openrefine.org/). I ran the cluster key collision,
   cluster levenshtein, cluster levenshtein with the radius updated to 2, and
the the cluster levenshetein with block 5.  I should have ran the cluster key
collsion in the `name_greper.py` script, as the OpenRefine cluster key
collision is not as good as can be created in python. The following
normalization function is much superior to the one found in OpenRefine. 

```python
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
[AmarnaNames4.csv](https://github.com/e2dubba/linked-amarna/blob/master/data/AmarnaNames4.csv).

3.
   [name_database_generator.py](https://github.com/e2dubba/linked-amarna/blob/master/scripts/name_database_generator.py).
This function imports yaml file that I created from looking at the index of
Moran's translation of the Amarna Letters, and Hess's Amarna personal names.
[The yaml file is in the data directory](https://github.com/e2dubba/linked-amarna/blob/master/data/WPACV.yml). This file also
imports the csv file created from OpenRefine.

4. [name_comparer.py](https://github.com/e2dubba/linked-amarna/blob/master/scripts/name_comparer.py) and
   [name_insert.py](https://github.com/e2dubba/linked-amarna/blob/master/scripts/name_insert.py) are used to improve the
database. The name_comparer finds additional clusters that might belong
together, these are updated with the name insert script. Additonal information
is added with the name insert script (like references to Hess's _Amarna
Personal Names_). 

5.
[d3_data_generator.py](https://github.com/e2dubba/linked-amarna/blob/master/scripts/d3_data_generator.py). This script generates
   the data used for the d3 visualization. The JSON file that is output from
this script should be adjusted so each of the top level keys become variables,
and the file needs to be renamed to `graph4.js`. This was for the purpose of
making the file easier to import into the html page.


## The Webpage 

[The Visualization is available here](site/index.html).

The resulting data visualization uses a [d3 force directed
graph](https://github.com/d3/d3-force). Also [fusejs](https://fusejs.io/) is
imported to allow for fuzzy searching of the names. 


## Bibliography 


- [Shlomo Izreel. _The Amarna
  Tablets_](https://www.tau.ac.il/humanities/semitic/amarna.html). The basis
of this project was manipulating Izreel's transcriptions to create a database
and explore it. 
- William L.F. Moran _The Amarna Letters_. Johns Hopkins University Press:
  Baltimore, 1992. I used the name index of Moran's book as the primary form
for each name, as well as additional information about the names (relations,
and scope notes). 
- Richard S. Hess. _Amarna Personal Names_. American Schools of Oriental
  Research Dissertation Series 9. Eisenbrauns; Winona Lake, 1993. All names
and references where checked against Hess's book. Izreel's reconstruction of
lacunae was kept. Also, much of the content of the scope notes goes back to
Hesses analysis. In addition, the language designation for each name is the
first language that Hess mentions. 
- Anson F Rainey. _The El-Amarna Correspondence_. Edited by William
  Schniedewind and Zipora Cochavi-Rainey. Handbook of Oriental Studies
  110. Brill: Leiden, 2015. Some of Izreel's transcriptions where checked
       against Rainey, but no new readings were adopted yet. 
