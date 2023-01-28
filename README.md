# AlbrechtPropExcavation
This repo holds all of the code needed to analyze data collected for the PROP_excavation trials

Contents
- [To Do List](#to-do)
- [General](#general)
- [Data Prep](#data-prep)
- [Code](#code)
- [Modeling](#modeling)

## TO DO
### General
1. Finish data analysis roadmap
2. Have meeting with Ute and Gabe
3. Determine how to structure the papers

### Data Prep
1. Separate all PROP_PICOS videos into individual frames
2. Re-measure angles of trees and make individual csv files.
3. Organize all data into sqlite database (this will be the most efficient for working with multiple tables of differing hierarchichal levels). We could have theorhetically store all of the datatypes in separate tables with the sys_id as the primary key
4. Data meeting with Gabe?

### Code
1. For the mixed model analysis, get all of the R code structured into one markdown file to be run. 
2. For the image analysis, much of the code needs to be refactored and tested

### Modeling
1. We should structure the modeling based on the paper that it will be published in. We need to figure out the paper structures first

|Data Type|Prop_ADAIR|PROP_PICOS|
|---------|----------|----------|
|1yr growth|X|Maybe Kim?|
|1yr canopy ratings|X|Maybe Kim?|
|2yr growth|X|X|
|2yr canopy ratings|X|X|
|2yr LAI|X|X|
|2yr HLB qPCR assay|X|X|
|Phytophthora assays|X||
|Leaf nutrient analysis|X|X|
|Soil nutrient analysis (bulk)|X|X|
|Soil moisture|X|X|
|Soil density|X|X|
|Rhizotron images|X||
|Manual root crown measurements|X|X|
|IMU sensor data|X||
|Excavation video footage|X|X|
|Force gauge data|X|X|
|Root crown vertical images|X|X|
|Root crown radial images|X|X|
