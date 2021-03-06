#!/usr/bin/env python
# coding: utf-8

# In[ ]:
# User Stories:

# 1) As a User I want to be able to identify the 10% of companies with a highest median Gender Pay Gap

# 2) As a User I want to be able to get the 10 companies with a median Gender Pay Gap closest to 0 so that
#    I can see which industries have minimised their Gender Pay Gap. 

# 3) As a User I want to be able to see how these 10 companies performed in the last few years so that I can
#    see the trends.

#Use SicCode as industry standard
#Run the analysis required 


from IPython.display import display
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
from tabulate import tabulate

warnings.simplefilter('ignore', FutureWarning)

START_YEAR = 2017
END_YEAR = 2020
STEP = 1
#Values are to be input here for desired time period and intervals.

print('\nThis analysis considers gender pay gaps at the company level from 2017 to 2020.\n')

END_YEAR1 = END_YEAR + 1
#Python ranges are not inclusive so this is required.

yearList = list(range(START_YEAR, END_YEAR1, STEP))
#List of all years.

dataURL = {}
for year in yearList:
    dataURL[year] = 'https://gender-pay-gap.service.gov.uk/viewing/download-data/' + str(year)
#Macro for data sources.

print('Data sources by year:')
for year in yearList:
    print(year, ':', dataURL[year])
#List of years and URLs. Allows for verifying that data sources are correctly specified.

# In[ ]:
data = {}
colCheck = {}
for year in yearList:
    data[year] = pd.read_csv(dataURL[year])
    colCheck[year] = data[year].columns

print('\nChecking data format is the same each year...')
for year in yearList:
    if colCheck[year].all() == colCheck[START_YEAR].all():
        print(year, ':', 'No data categorisation issues.')
        mergedDataAll = pd.concat([data[year] for year in yearList])
        #Merges all data into one dataset.
    else:
        print('Data is formatted differently across years.')
#Checks column headers are exactly identical over time.
#If this was not the case, would need to consider how to merge datasets containing
#similar data under different headings.

# In[ ]:
COLUMNS = ['EmployerName', 'SicCodes', 'DiffMedianHourlyPercent', 'DueDate']
mergedData = mergedDataAll[COLUMNS]
#Macros for columns relevant to analysis.
print('\nChecking for missing data...')
if mergedData.equals(mergedData.dropna()) is False:
    print('There is missing data for key variables; these records have been deleted.')
    mergedData = mergedData.dropna()
else:
    print('No missing data for key variables.')
#If there is missing data for key variables, these must be excluded from the analysis.

# In[ ]:
#Many of the SIC codes are formatted incorrectly, and have extra characters/are too short;
# only last 5 digits are required.

print('\nChecking industry SIC Codes are correctly formatted:')
if all(mergedData['SicCodes'].str.len() == 5) & all(mergedData['SicCodes'].str.isdecimal()):
    print('\nSIC Codes are correctly formatted.')
else:
    print('\nSIC Codes are not correctly formatted; reformatting...')

# In[ ]
if all(mergedData['SicCodes'].str.isdecimal()):
    print('SIC Codes contain only numeric characters as required.')
else:
    mergedData.loc[:, 'SicCodes'] = mergedData['SicCodes'].map(lambda x: ''.join([y for y in x if y.isdigit()]))
    print('SIC Codes contain non-numeric characters; these have been deleted.')

# In[ ]:
if all(mergedData['SicCodes'].str.len() == 5):
    print('SIC Codes are all the correct length.')
else:
    mergedData.loc[:, 'SicCodes'] = mergedData['SicCodes'].str[-5:]
    mergedData = mergedData[mergedData['SicCodes'].apply(lambda x: len(x) == 5)]
    print('SIC Codes are too long or too short; codes have been cut to 5 digits or deleted if too short.')
mergedData = mergedData[mergedData['SicCodes'] != 99999]
#Deletes records of dormant companies.
print('\nSIC Codes are now correctly formatted.')

# In[ ]:
print('\nThe data will be considered on a yearly basis, where year denotes the year in which the period started.\n')
mergedData.loc[:, 'DueDate'] = mergedData['DueDate'].str[6:10].astype(int)
mergedData['DueDate'] = mergedData['DueDate'] - 1
#Formats Due Date as a date and time, converts into starting year only.

# In[ ]:
display(mergedData['DueDate'].value_counts())
print('\nOnly 12 observations for 2020; these will be disregarded. Sample size too small for meaningful inference.')
mergedData = mergedData[mergedData['DueDate'] != 2020]

# In[ ]:

yearList = list(range(START_YEAR, END_YEAR, STEP))
def pprint(dframe):
    print(tabulate(dframe.head(10), headers='keys', tablefmt='psql', showindex=False))
def pprintindex(dframe):
    print(tabulate(dframe, headers='keys', tablefmt='psql'))
mergedData['modGap'] = mergedData['DiffMedianHourlyPercent'].abs().copy()
data = {}
highestDecileMen = {}
n = 10

print('\n1st decile employers with the largest proportional wage gap where men earn more, by year (first 10 shown only):')
for year in yearList:
    data[year] = mergedData[mergedData['DueDate'] == year]
    data[year] = data[year].sort_values(['DiffMedianHourlyPercent'], ascending=False)
    highestDecileMen[year] = data[year].head(int(len(data[year]['DiffMedianHourlyPercent'])*(n/100)))
    highestDecileMen[year] = highestDecileMen[year][['EmployerName', 'DiffMedianHourlyPercent']]
    highestDecileMen[year].columns = ['Employer', 'Median Hourly Wage Gap (Men)']
    print('\n',year,':\n')
    pprint(highestDecileMen[year])

# In[ ]:
#May also consider top 10% largest proportional gaps, but bi-directional.

highestDecileAny = {}
#mergedData['modGap'] = mergedData['DiffMedianHourlyPercent'].abs()

print('\n1st decile employers with the largest proportional wage gap where men or women earn more, by year (first 10 shown only):')

for year in yearList:
    data[year]['modGap'] = data[year]['DiffMedianHourlyPercent'].abs()
    data[year] = data[year].sort_values(['modGap'], ascending=False)
    highestDecileAny[year] = data[year].head(int(len(data[year]['modGap'])*(n/100)))
    highestDecileAny[year] = highestDecileAny[year][['EmployerName', 'modGap', 'DiffMedianHourlyPercent']]
    
    conds = [
        (highestDecileAny[year]['DiffMedianHourlyPercent'] > 0),
        (highestDecileAny[year]['DiffMedianHourlyPercent'] < 0),
        (highestDecileAny[year]['DiffMedianHourlyPercent'] == 0)
    ]
    
    outs = ['Men', 'Women', 'No Gap']
    
    highestDecileAny[year]['DiffMedianHourlyPercent'] = np.select(conds, outs)
    highestDecileAny[year].columns = ['Employer', 'Median Hourly Wage Gap (all)', 'Earns More']
    print('\n',year,':\n')
    pprint(highestDecileAny[year])

# In[ ]:
#Now can find 10 employers with smallest gap.
#There are >10 with a gap of 0.0%; this could be due to reporting or measurement error.
#Regardless, it is not representative to only select 10. All with a zero gap will be included here.

smallestGap = {}

print('\nEmployers with reported median wage gap of zero, by year (first 10 shown only):')

for year in yearList:
    smallestGap[year] = data[year][data[year]['modGap'] == int(0)]
    smallestGap[year] = smallestGap[year][['EmployerName', 'modGap']]
    smallestGap[year].columns = ['Employer', 'Median Hourly Wage Gap (all)']
    print('\n',year,':\n')
    pprint(smallestGap[year])

# In[ ]:
#Defining Industries.
mergedData['SicCodes'] = mergedData['SicCodes'].astype(int)

conditions = [
    (mergedData['SicCodes'] <= 3220),
    ((mergedData['SicCodes'] >= 5101) & (mergedData['SicCodes'] <= 9900)),
    ((mergedData['SicCodes'] >= 10110) & (mergedData['SicCodes'] <= 33200)),
    ((mergedData['SicCodes'] >= 35110) & (mergedData['SicCodes'] <= 35300)),
    ((mergedData['SicCodes'] >= 36000) & (mergedData['SicCodes'] <= 39000)),
    ((mergedData['SicCodes'] >= 41100) & (mergedData['SicCodes'] <= 43999)),
    ((mergedData['SicCodes'] >= 45111) & (mergedData['SicCodes'] <= 47990)),
    ((mergedData['SicCodes'] >= 49100) & (mergedData['SicCodes'] <= 53202)),
    ((mergedData['SicCodes'] >= 55100) & (mergedData['SicCodes'] <= 56302)),
    ((mergedData['SicCodes'] >= 58110) & (mergedData['SicCodes'] <= 63990)),
    ((mergedData['SicCodes'] >= 64110) & (mergedData['SicCodes'] <= 66300)),
    ((mergedData['SicCodes'] >= 68100) & (mergedData['SicCodes'] <= 68320)),
    ((mergedData['SicCodes'] >= 69101) & (mergedData['SicCodes'] <= 75000)),
    ((mergedData['SicCodes'] >= 77110) & (mergedData['SicCodes'] <= 82990)),
    ((mergedData['SicCodes'] >= 84110) & (mergedData['SicCodes'] <= 84300)),
    ((mergedData['SicCodes'] >= 85100) & (mergedData['SicCodes'] <= 85600)),
    ((mergedData['SicCodes'] >= 86101) & (mergedData['SicCodes'] <= 88990)),
    ((mergedData['SicCodes'] >= 90010) & (mergedData['SicCodes'] <= 93290)),
    ((mergedData['SicCodes'] >= 94110) & (mergedData['SicCodes'] <= 96090)),
    ((mergedData['SicCodes'] >= 97000) & (mergedData['SicCodes'] <= 98200)),
    (mergedData['SicCodes'] == 99000)

]

output1 = [
    'Agriculture, Forestry and Fishing',
    'Mining and Quarrying',
    'Manufacturing',
    'Electricity, gas, steam and air conditioning supply',
    'Water supply, sewerage, waste management and remediation activities',
    'Construction',
    'Wholesale and retail trade; repair of motor vehicles and motorcycles',
    'Transportation and storage',
    'Accommodation and food service activities',
    'Information and communication',
    'Financial and insurance activities',
    'Real estate activities',
    'Professional, scientific and technical activities',
    'Administrative and support service activities',
    'Public administration and defence; compulsory social security',
    'Education',
    'Human health and social work activities',
    'Arts, entertainment and recreation',
    'Other service activities',
    'Activities of households as employers; undifferentiated goods and services producing activities of households for own use',
    'Activities of extraterritorial organisations and bodies'
]

output2 = list(range(1, 22))

mergedData['Industry'] = np.select(conditions, output1)
mergedData['Industry ID'] = np.select(conditions, output2).astype(int)
mergedData = mergedData[mergedData['SicCodes'] != 99999]
mergedData = mergedData.drop(mergedData[mergedData['SicCodes']==99999].index)
mergedData = mergedData[mergedData['Industry'] != 0]
mergedData = mergedData.drop(mergedData[mergedData['Industry']==0].index)

# In[ ]:
medians = mergedData.groupby('Industry').median()
medians = medians[['DiffMedianHourlyPercent', 'Industry ID']].sort_values('DiffMedianHourlyPercent')
bestIDs = list(medians['Industry ID'].head(10))
medians = medians[['DiffMedianHourlyPercent']]
medians.columns = ['Median Hourly Wage Gap (Men)']
print('\nTable displaying 10 industries with the smallest median pay gap over the whole period:\n')
pprintindex(medians.head(10))
# In[ ]:


# In[ ]:
barChart1 = medians.head(10).plot(y = 'Median Hourly Wage Gap (Men)', grid=True, kind='bar', legend=False, figsize=(10,5))
barChart1.set(xlabel = "Industry", ylabel = 'Median Hourly Wage Gap (Men)')
print('\nBar chart comparing median pay gap across these 10 industries over the whole period:\n')
plt.show()

# In[ ]:
mergedData.columns = ['EmployerName', 'SicCodes', 'Median Hourly Wage Gap (Men)', 'Year', 'modGap', 'Industry', 'Industry ID']
medians2 = mergedData.groupby(['Industry', 'Year']).median()
medians2 = medians2[['Median Hourly Wage Gap (Men)']].sort_values('Median Hourly Wage Gap (Men)')
medians2.columns = ['Median Hourly Wage Gap (Men)']
print('\nTable displaying 10 industry-years with the smallest median pay gap:\n')
pprintindex(medians2.head(10))

# In[ ]:
mergedData.columns = ['EmployerName', 'SicCodes', 'Median Hourly Wage Gap (Men)', 'Year', 'modGap', 'Industry', 'Industry ID']
medians2 = mergedData[mergedData['Industry ID'].isin(bestIDs)].groupby(['Industry', 'Year']).median()
medians2 = medians2[['Median Hourly Wage Gap (Men)']].unstack()
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print('\nTable displaying yearly median pay gap in 10 best industries:\n')
display(medians2)

# In[ ]:
medians2 = mergedData[mergedData['Industry ID'].isin(bestIDs)].groupby(['Year', 'Industry']).median()
medians2 = medians2[['Median Hourly Wage Gap (Men)']].unstack()
lineGraph = medians2.plot(y = 'Median Hourly Wage Gap (Men)', grid=True, kind='line', figsize=(15,10))
lineGraph.set_ylabel('Median Hourly Wage Gap (Men)')
lineGraph.legend(loc='center left',bbox_to_anchor=(1.0, 0.5))
print('\nLine graph of median pay gap over time in these 10 industries:\n')
plt.show()

# In[ ]:
print('\nExtensions:')
print('- The variance of the pay gap could be considered across industries.')
print('- In conjunction with sample size, hypothesis testing could then be conducted to determine if the pay')
print('   gap is significant.')
print('- A regression analysis including covariates that can be observed in the data set e.g. company size would be')
print('   more informative of the type of companies which tend to have smaller or larger pay gaps.')
