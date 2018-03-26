#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Copyright (C) 2017 Bitergia
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Authors:
##   Jesus M. Gonzalez-Barahona <jgb@bitergia.com>
##   Keanu Nichols
## Some simple examples for exploring how to work with pandas
## and GrimoireLab indexes.

from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import elasticsearch_dsl
import pandas as pd
import numpy as np
from pprint import pprint


def perceval_elasticsearch_git_dsl_2(es):
	# Build a DSL Search object on the 'commits' index, 'summary' documents type
	request = elasticsearch_dsl.Search(using=es, index='commits',
		                            doc_type='summary')
	# We need to request only some fields
	request = request.source(['author'])

	# Run the Search, using the scan interface to get all resuls
	response = request.scan()
	d={}
	#print("sigh")
	#Creates a dictionary and then adds a counter for each of them in the dictionary
	for commit in response:
		if(commit.author not in d):
			d[commit.author] = 1;
		else:
			d[commit.author]+=1;			
		
	#print("\n\n")
	return d

es = Elasticsearch('http://localhost:9200', verify_certs=False)

# Buckets by author name, finding first commit for each of them
s = Search(using=es, index='git')
s.aggs.bucket('by_authors', 'terms', field='author_name', size=10000) \
    .metric('first_commit', 'min', field='author_date')
s = s.sort("author_date")
result = s.execute()

# Uncomment the following two lines to see the resutls obtained
# from the query
#from pprint import pprint
#pprint(result.to_dict())

# Get a dataframe with each author and their first commit
buckets_result = result['aggregations']['by_authors']['buckets']
buckets = []
for bucket in buckets_result:
    first_commit = bucket['first_commit']['value']/1000
    buckets.append(
        {'first_commit': datetime.utcfromtimestamp(first_commit),
        'author': bucket['key']}
        )
authors = pd.DataFrame.from_records(buckets)
authors.sort_values(by='first_commit', ascending=False, inplace=True)
#pprint(authors)

d = perceval_elasticsearch_git_dsl_2(es)

total = 0


'''Creates a dataframe for the commits for the new authors, the name of the authors,
   and the day they first committed to the repository'''
df = pd.DataFrame(columns=['Commits','Author','Date'])
for i in range(len(authors.author)):
	for k in list(d.keys()):
		if(authors.author[i] in k) :
			df.loc[i] = [d[k],authors.author[i],authors.first_commit[i]]
			total+=d[k]
			break

df.sort_values(by='Date', ascending=False, inplace=True)

#Creates a new dataframe to have more specific information about the new committer
df1 = pd.DataFrame(columns=['Year','Month','Commits','Author','Date'])
for i in range(len(authors.author)):
	for k in list(d.keys()):
		if(authors.author[i] in k) :
			df1.loc[i] = [authors.first_commit[i].year,authors.first_commit[i].month,
				d[k],authors.author[i],authors.first_commit[i],]
			total+=d[k]
			break
df1.sort_values(by='Date', ascending=True, inplace=True)
#df1 = df1.drop('Date', 1)
df1.rename(columns={'Date': 'New'}, inplace=True)
k = 0

temp = authors['first_commit'] \
    .groupby([authors.first_commit.dt.year,
            authors.first_commit.dt.month]) \
    .agg('count')

by_month = df1 \
    .groupby([df1.Year,
            df1.Month,df1.Author,df1.Commits]) \
    .agg('count')

by_month['New'] = by_month['New'].astype(str)

df1 = df1.reset_index(drop=True)
i=0
by_month['New'] = 'a'
while(i<len(temp)):
	val1 = val2 = False
	if(k>0 and k<len(authors.author)-1):
		val1 = (df1.Year[k] == df1.Year[k-1]) 
		val2 = (df1.Month[k] == df1.Month[k-1])
		if(val1 == True and val2 == False or val1 == False and val2 == False):	
			by_month['New'][k] = str(temp[i])
		else:
			by_month['New'][k] = " "
			i-=1
	else:
		if(k==0):
			by_month['New'][k] = str(temp[i])
		else:
			val1 = (df1.Year[k] == df1.Year[k-1]) 
			val2 = (df1.Month[k] == df1.Month[k-1])
			if(val1 == True and val2 == False or val1 == False and val2 == False):	
				by_month['New'][k] = str(temp[i])
			else:
				by_month['New'][k] = " "
				i-=1
	k+=1
	i+=1

for i in range(len(by_month['New'])):
	if (by_month['New'][i]=='a'):
		by_month['New'][i] = " "
#by_month['New'][2] = '\0'
by_month.rename(columns={'New': 'New Committers'}, inplace=True)
print(by_month, "\n\n")
#result = df1.append(by_month, ignore_index=True)

# Uncomment the following line (and the import of pprint, above)ç
# to print the dataframe,
#pprint(authors)


#print(by_month)
# Produce csv files
print("Creating CSV for new authors and commits")
by_month.to_csv('final.csv')
