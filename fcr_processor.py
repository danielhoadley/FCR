from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
import os

# Create connection to MongoDB

client = MongoClient('localhost', 27017)
db = client['caselaw']
collection = db['FCR']

# Set the working directory

directory = '/Users/danielhoadley/Documents/Development/FCR/Source-XML/family_court_reports'

# Open .xml files

for filename in os.listdir(directory):
    if filename.endswith('.xml'):

        document = open(filename, 'r')

        #Parse each .xml file
        soup = BeautifulSoup(document, 'lxml')

        #print (soup)

        # Get the case name
        case_name = soup.find('case')
        # Get the court
        courttag = soup.find('para')
        court = courttag.text
        # Get the date
        date = soup.find(string=re.compile("\d\d\d\d\d\d\d\d"))
        # Get the FCR ref
        ref = soup.find(string=re.compile("(FCR)"))
        # Get the subject matter
        sm = soup.find(string=re.compile("(–|&#x2013;)"))
        # Get the Ncit
        ncit = soup.find(string=re.compile("(EWHC|EWCA|UKSC)"))
        # Get word count of case
        case_text = soup.text
        wordCount = len(case_text.split())
        # Sort out court field
        if 'FamD' in court:
            court = 'FD'
        if 'CACivD' in court:
            court = 'CA'
        if 'CACiv' in court:
            court = 'CA'
        if 'CACrimD'in court:
            court = 'CA'
        if 'ChD' in court:
            court = 'Ch D'
        if 'AdminCt' in court:
            court = 'QBD'
        if 'UKSC' in court:
            court = 'SC'
        if 'FamCt' in court:
            court = 'Fam Ct'
        if 'EUCJ' in court:
            court = 'ECJ'
        if 'EctHR' in court:
            court = 'ECtHR'
        if '255' in court:
            court = ''
# Remove stray captures in court field: any string greater than 6 chars in length
        if len(court) > 6:
            court = ''
# Suppress false positives in sm
        if sm == None:
            sm = 'None'
        if len(sm) < 40:
            sm = ''
# Clean the ncit
        if ncit == None:
            ncit = ''
        if len(ncit) > 22:
            ncit = ncit[:23]
# Convert date string to YYYY-mm-dd format
        if date == None:
            print ("nodate")
        else:
            fdate = "{}-{}-{}".format(date[4:], date[2:4], date[0:2])
# Check FCR ref
        if ref is None:
            ref = ''
        if 'FCR' in ref:
            ref = ref
        else:
            ref = ''

        print ('\n******', filename, '*******\n')

        print ('  ',case_name.text)
        print ('  ', ncit)
        print ('  ', ref)
        print ('  ',court)
        print ('  ',fdate)
        print ('  ',sm)

        #print (wordCount)
        #print (count)

        content = str(soup)

# Build dictionary for each case
        d = {'Source_File': filename, 'CaseName': case_name.text, 'NeutralCitation': ncit, 'PubRef': ref, 'Court': court, 'Date': fdate, 'SubjectMatter': sm,'wordCount': wordCount, 'Content': content}

        #print ('\n', d)
# Insert dictionary into MongoDB
        collection.insert(d)

