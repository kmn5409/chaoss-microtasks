#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Copyright (C) 2016 Bitergia
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
##

import elasticsearch
import elasticsearch_dsl
from elasticsearch_dsl import Search
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
# ElasticSearch instance (url)
es = elasticsearch.Elasticsearch(['http://localhost:9200/'])

# Build a DSL Search object on the 'github' index, 'summary' documents type
s = Search(using=es, index='github')

s = s.source(['created_at', 'time_to_close_days', 'time_open_days','closed_at',
              'id_in_repo'])

# As we are only looking for issues, we shall specify that in "item_type"
s = s.filter('terms', item_type=['issue'])

# We are looking for all the issues that were created in the last 6 months.
s = s.filter('range', created_at={'gte' : 'now-6M'})

# And we are going to arrange all these documents according to when they were created in ascending order
s = s[0:1500]
s = s.sort({'created_at': { 'order' : 'asc'}})


result = s.execute()
#result = result.to_dict()['hits']['hits']
#print(result)
result = result.to_dict()['hits']['hits']
issues = [issue['_source'] for issue in result]

issues = pd.DataFrame(issues)

# We fill all the NaN values with zero
issues = issues.fillna(0)
print(issues)
# Run the Search, using the scan interface to get all resuls

plt1 = issues.plot(x=issues['id_in_repo'], kind='bar', figsize=(20,15), title ="Issues in the last 6 months", legend=True, fontsize=12)
plt1.set_ylabel("Number of Days", fontsize=12)
plt1.set_xlabel("Issue Id in repo", fontsize=12)
fig1 = plt.gcf()
plt.show()
plt.draw()
fig1.savefig('test.png', dpi=100)
