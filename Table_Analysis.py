#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:


import camelot
import tabula 
import pandas as pd
import pymongo
import json 
import numpy as np
import re
from collections import Counter
import pdfquery
import tika
from itertools import groupby
import fitz


# In[ ]:


elements_list=['Hydrogen','Helium','Lithium','Beryllium','Boron','Carbon','Nitrogen','Oxygen','Fluorine','Neon','Sodium',
 'Magnesium','Aluminium','Silicon','Phosphorus','Sulphur','Chlorine','Argon','Potassium','Calcium','Scandium','Titanium','Vanadium','Chromium',
 'Manganese','Iron','Cobalt','Nickel','Copper','Zinc','Gallium','Germanium','Arsenic','Selenium','Bromine','Krypton','Rubidium',
 'Strontium','Yttrium','Zirconium','Niobium','H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si',
 'P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br',
 'Kr','Rb','Sr','Y','Zr','Nb','Molybdenum','Technetium','Ruthenium','Rhodium','Palladium','Silver','Cadmium',
 'Indium','Tin','Antimony','Tellurium','Iodine','Ytterbium','Zinc','Zirconium','Drill', 'Hole','DDH holes','RC holes']


# In[ ]:


len(elements_list)


# In[ ]:


client=pymongo.MongoClient('mongodb://127.0.0.1:27017/')
database=client['Table_database']
table_data=database.collection_name


# In[ ]:


df=pd.read_csv("table - Sheet1.csv")
df.head()


# In[ ]:


tables = camelot.read_pdf(r'file:///C:/Users/sharm/OneDrive/Desktop/r1000/r1000/00584709-00000009-00004762-SEDAR@%23wlrtech.pdf'
                          ,pages='1-end',flavor='lattice',copy_text=['v','h'])
tables


# In[ ]:


print(tables[0].parsing_report)
page=tables[5].parsing_report['page']
page_num=int(page)
print(page_num)


# In[ ]:



## Checking whether the table is empty or not !!!
##empty_table will return true if it is empty else it will return false 
empty_table=True
df=tables[5].df
df_orig=df
df

for i in df.loc[0]:
    if i!='':
        empty_table=False
        break
empty_table        



## cheching for the header 

table_header=""
if("Table" in df.loc[0][0]):
    table_header=df.loc[0][0]
    df=df.drop(index=0) 
    



## cheching whether the tbale is of use or not by identifying key elemtns !
table_use=False
matches=[]
if table_header !="":
    sentence=table_header.split()
    for i in sentence:
        if i in elements_list:
            matches.append(i)
            break
    if len(matches)!=0:
         table_use=True

            
if table_use== False:
    for i in df.iloc[0]:
        sentence=i.split()
        for i in sentence:
            if i in elements_list:
                matches.append(i)
                break
        if len(matches)!=0:    
            table_use=True
            break

if table_use==False:
        rows=df.shape[0]
        for i in range(1,rows):
            for j in df.iloc[i]:
                  if j in elements_list:
                        matches.append(j)
                        break
            if len(matches)!=0:
                table_use=True
                break


bounding_box=tables[5]._bbox   ## Bottom_left_x, Boottom_left_y, top_right_X, top_right_y
bounding_box

upper_text_rect=[] ##
lower_text_rect=[] ## 

upper_text_rect.append(bounding_box[0]-20)
upper_text_rect.append(792-bounding_box[3]-150)
upper_text_rect.append(bounding_box[2]+20)
upper_text_rect.append(792-bounding_box[3])
print(upper_text_rect) # contains the rectange top left x, top left y, bottom rightx, bottom right y in this order only

lower_text_rect.append(bounding_box[0]-20)
lower_text_rect.append(792-bounding_box[1]+20)
lower_text_rect.append(bounding_box[2]+20)
lower_text_rect.append(792-bounding_box[1]+20+150)
print(lower_text_rect)


## Extracting text above the table :

rect=upper_text_rect  # rect list two
doc = fitz.open(r"00584709-00000009-00004762-SEDAR@#wlrtech.pdf")  # any supported document type

## fitz follow zero based indexing of page thats why we need subtracted one !!
page = doc[page_num-1]   # we want text from this page
page
words = page.getText("words")  # list of words on page
words.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x coordinate

mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
group = groupby(mywords, key=lambda w: w[3])

upper_text=""

print("\nSelect the words intersecting the rectangle")
print("-------------------------------------------")
for y1, gwords in group:
    a=" ".join(w[4] for w in gwords)
    print(a)
    upper_text=upper_text+a+" " 

## If table is at the top then we need to extract text from previous page  
if(upper_text==""):
    rect=[bounding_box[0]-20,692,bounding_box[2]+20,750]
    doc = fitz.open(r"00584709-00000009-00004762-SEDAR@#wlrtech.pdf")  # any supported document type
    page_num_previous=page_num-1-1
    page = doc[page_num_previous]   # we want text from this page
    words = page.getText("words")  # list of words on page
    words.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x coordinate

    mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
    group = groupby(mywords, key=lambda w: w[3])
    print("\nSelect the words intersecting the rectangle")
    print("-------------------------------------------")
    for y1, gwords in group:
        a=" ".join(w[4] for w in gwords)
        print(a)
        upper_text=upper_text+a+" " 

    

## Extracting text below the table :

rect=lower_text_rect  # rect list two
doc = fitz.open(r"00584709-00000009-00004762-SEDAR@#wlrtech.pdf")  # any supported document type
page = doc[page_num-1]   # we want text from this page
page
words = page.getText("words")  # list of words on page
words.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x coordinate

mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
group = groupby(mywords, key=lambda w: w[3])
lower_text=""
print("\nSelect the words intersecting the rectangle")
print("-------------------------------------------")
for y1, gwords in group:
    a=" ".join(w[4] for w in gwords)
    print(a)
    lower_text=lower_text+a+" " 

## If table is at the bottom then we need to extract text from next page  
if(lower_text==""):
    rect=[bounding_box[0]-20,0,bounding_box[2]+20,150]
    doc = fitz.open(r"00584709-00000009-00004762-SEDAR@#wlrtech.pdf")  # any supported document type
    page_num_next=page_num-1+1
    page = doc[page_num_next]   # we want text from this page
    page
    words = page.getText("words")  # list of words on page
    words.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x coordinate

    mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
    group = groupby(mywords, key=lambda w: w[3])
    b=""
    print("\nSelect the words intersecting the rectangle")
    print("-------------------------------------------")
    for y1, gwords in group:
        a=" ".join(w[4] for w in gwords)
        print(a)
        lower_text=lower_text+a+" " 

    

df=df_orig
table_header=""
if("Table" in df.loc[0][0]):
    table_header=df.loc[0][0]
    df=df.drop(index=0)
    flag=True
    for i in df.loc[2]:
        if( not (bool(re.search('[a-zA-Z]', i)) or i=="")):
                flag=False
                break
                
    if(flag==True):
        j=0
        for i in df.loc[1]:   
            if df.loc[1][j]!=df.loc[2][j]:
                df.loc[1][j]=i+'-'+df.loc[2][j]
            
            df.loc[1][j]=df.loc[1][j].replace('.','')      
            j =j+1
        df=df.rename(columns=df.loc[1])   
        df=df.drop(index=[1,2])

    else: 
        df=df.rename(columns=df.loc[1])   
        df=df.drop(index=[1])
        
else:
    flag=True
    for i in df.loc[1]:
        if( not (bool(re.search('[a-zA-Z]', i)) or i=="")):
            flag=False
            break
            
    if(flag==True):
        j=0
        for i in df.loc[0]:
            if df.loc[0][j]!=df.loc[1][j]:
                  df.loc[0][j]=i+'-'+df.loc[1][j]
            
            df.loc[0][j]=df.loc[0][j].replace('.','')  
            j=j+1 
        df=df.rename(columns=df.loc[0])
        df=df.drop(index=[0,1])
    
    else:  
        
        df=df.rename(columns=df.loc[0])
        df=df.drop(index=[0])
      
                
final_columns=[]
for i in df.columns:
    final_columns.append(i.replace('.',''))
df.columns=final_columns 
        


new_columns=[]
flag_1=False
for i in df.columns:
    if(columns_freq_dict[i]>1):
        flag_1=True
        a=(i+'_'+str(ses[i])).replace(".","")
        new_columns.append(a)
        ses[i]=ses[i]+1 
    else:
            a=i.replace(".",'')
            new_columns.append(i)
if(flag_1==True):
     df.columns=new_columns
     
     
        
