# Amarna Personal Names

Tools and results from parsing Shlomo Izre'el's transcriptions of the Amarna
Letters. [Izre'el's transcriptions can be found
here](https://www.tau.ac.il/humanities/semitic/amarna.html). 

[Linked Amarna](site/index.html)


## Process for Data Collection and Curation

Order of Scripts:
1. [name_greper.py](https://github.com/e2dubba/linked-amarna/blob/master/scripts/name_greper.py). This script downloads the text
   from Shlomo Izre'el's website, or uses a text file stored locally. It then
prepares and generates the basic table for the database, as well as creates an
Excel file that can be imported into OpenRefine. The columns might need to be
adjusted in the Excel file to make them easier to work with.

2. [OpenRefine](https://openrefine.org/). I ran the cluster key collision,
   cluster levenshtein, cluster levenshtein with the radius updated to 2, and
the cluster levenshetein with block 5.  I should have ran the cluster key
collision in the `name_greper.py` script, as the OpenRefine cluster key
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

3. [name_database_generator.py](https://github.com/e2dubba/linked-amarna/blob/master/scripts/name_database_generator.py).
This function imports yaml file that I created from looking at the index of
Moran's translation of the Amarna Letters, and Hess's Amarna personal names.
[The yaml file is in the data directory](https://github.com/e2dubba/linked-amarna/blob/master/data/WPACV.yml). This file also
imports the csv file created from OpenRefine.

4. [name_comparer.py](https://github.com/e2dubba/linked-amarna/blob/master/scripts/name_comparer.py)
collects text variants in the database, and offers suggestions for linking
canonical forms of the name to the text line. 
[name_insert.py](https://github.com/e2dubba/linked-amarna/blob/master/scripts/name_insert.py)
was used to expand the name information, also added additional information
like reference to Hess's _Amarna Personal Names_.

5. [d3_data_generator.py](https://github.com/e2dubba/linked-amarna/blob/master/scripts/d3_data_generator.py).
This script generates the data used for the d3 visualization. The JSON file
that is output from this script should be adjusted so each of the top level
keys become variables, and the file needs to be renamed to `graph4.js`. This
was for the purpose of making the file easier to import into the html page.

## The Linked Amarna Visualization 

[The Visualization is available here](site/index.html).

### Using the Visualization

The left hand panel contains a list of all of the names that are found in the
database. Click on any of the names to display the sub graph of names
connected to that person. The links between names shows that there is at least
one text where both names are found. The left panel also has a search box
where any form of the name can be searched, all of the transcriptions, and
various spellings can be searched. 

After a name is selected, a info box will appear in the bottom right hand
corner. This info box can be expanded to show more information about the
individual. 

In the top right corner of the visualization is a toggle switch which will
expand any subgraph to include friend of a friend relations. This will allow
the user to see how an individuals network fits in the greater corpus. 

### About the Coding of the Visualization 

The resulting data visualization uses a [d3 force directed
graph](https://github.com/d3/d3-force). Also [fusejs](https://fusejs.io/) is
imported to allow for fuzzy searching of the names. 

## Bibliography 

- [Shlomo Izre'el. _The Amarna
  Tablets_](https://www.tau.ac.il/humanities/semitic/amarna.html). The basis
of this project was manipulating Izre'el's transcriptions to create a database
and explore it. 
- William L.F. Moran _The Amarna Letters_. Johns Hopkins University Press:
  Baltimore, 1992. I used the name index of Moran's book as the primary form
for each name, as well as additional information about the names (relations,
and scope notes). 
- Richard S. Hess. _Amarna Personal Names_. American Schools of Oriental
  Research Dissertation Series 9. Eisenbrauns; Winona Lake, 1993. All names
and references where checked against Hess's book. Izre'el's reconstruction of
lacunae was kept. Also, much of the content of the scope notes goes back to
Hess's analysis. In addition, the language designation for each name is the
first language that Hess mentions. 
- Anson F Rainey. _The El-Amarna Correspondence_. Edited by William
  Schniedewind and Zipora Cochavi-Rainey. Handbook of Oriental Studies 110.
Brill: Leiden, 2015. Some of Izre'el's transcriptions where checked against
Rainey, but no new readings were adopted yet. 

