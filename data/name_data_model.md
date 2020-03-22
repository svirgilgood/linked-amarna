# Data Modeling for Amarna Personal Names 


## Tables 

The following are the tables and names for the Amarna Database.

### Context And Name Normalizing 

Columns:
- Column (PRIMARY KEY)
- reference
- text
- name
- normalized
- cluster_key_collision
- cluster_levenshtein
- cluster_levenshtein_radius2
- cluster_levenshtein_block5

### Canonical Name 

Columns:
- Primary Key 
- Moran Name 
- SN (Scope Note) 
- Language
- Location (Currently blank) 

### Name Variants

Columns:
- Canonical Name Key
- Name Variation 
- Source (?) 


### Related Terms 

Columns:
- Canonical Name Key 
- Relation
- Related Name Key 
- Related Name Form 

### Text and People

Columns:
- Text (EA Number) 
- Relationship (wrote, recieved, mentioned_in)
- Canoncial Name Key



