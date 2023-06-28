# Project name
Author(s): Corey Barrit, Harry Eslick
Creation date: eg. 2023-06-28 

## Project description:   
Code for automating the conversion of David's hand draw field data.
   
Inputs: 
- Hand drawn point vector data
- Hand drawn polygon vector data
- plantation layer to map the hand drawn data onto

Outputs: 
- hand drawn layers converted to plantations crs.
- plantations layer with pest data from hand drawn layers.
  

## Additional notes:   
This job has been quite confusing to implement and therefore it is hard to comprehend and make changes to. Sorry.
  
## Scripts:   
FieldRecord.py:   
Description: Main script.
Inputs:
- input vector layers listed above.
- set project crs

src.decode.py:   
Description: Takes CODEs in original format 'DB_Low_Med_' and converts to dictionary {'DB': ['Low', 'Med']}

src.formatting.py:   
Description: 
- Converts dictionary format to final dataframe format. 
- DB & SN gets their own column. 
- Abiotic pests have a column.
- all other pests go into their own column
- severities for DB & SN go into the DB & SN columns.
- all other severities go into the severity column.

src.process_points.py:   
Description: Intersects the hand drawn points layer with plantations layer. Also has the polygon/points merging function.

src.process_polygons.py:   
Description: Intersects the hand drawn polygons layer with the plantations layer.

src.utils.py:   
Description: Functions for setup of script (reading, setting crs, etc), and other misc. functions.


""   

""   

## Installation Instructions   
Coming soon...

## Style Guide
Basic [PEP-8](https://www.python.org/dev/peps/pep-0008/)
* CamelCase for classes  
* snake_case for functions  
* Prefer import module; module.func over from module import func; func for clarity on origin of the function  
* Docstrings in numpy format  
* Type hints for function definitions  

