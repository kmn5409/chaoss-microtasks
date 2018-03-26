from perceval.backends.core.github import GitHub
import elasticsearch
from datetime import date
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt

def isrecent(issues,d1,dicti):
	temp = issues.split("-")
	year = int(temp[0])
	month_num = int(temp[1])
	day = int(temp[2][:2])
	if(date(int(d1[0]),int(d1[1]),int(d1[2])) < date(year,month_num,day)):
		dicti[month_num]+=1
		return True
	return False

# Url for the git repo to analyze
#repo_url = 'https://github.com/chaoss/grimoirelab-perceval'
repo_url = 'grimoirelab-perceval'
# Directory for letting Perceval clone the git repo
repo_dir = 'grimoirelab-perceval'
token = -XXX
own = 'chaoss'
# ElasticSearch instance (url)
es = elasticsearch.Elasticsearch(['http://localhost:9200/'])
#repo = 'grimoirelab-perceval'

# Create the 'commits' index in ElasticSearch
es.indices.create('issues')
# Create a Git object, pointing to repo_url, using repo_dir for cloning
repo = GitHub(owner=own,repository=repo_url,api_token=token)
# Fetch all commits as an iteratoir, and iterate it uploading to ElasticSearch
i=1
closed = 1
open1 = 1
date1 = date.today() + relativedelta(months=-5)
date1 = str(date1)
print(date1)
d1 = date1.split("-")
print(d1[1])
mon = []
opn = {}
clo = {}
#plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
#plt.show()
for i in range(6):
	if(int(d1[1])+i<13):
		opn[int(d1[1])+i] = 0
		clo[int(d1[1])+i] = 0
		mon.append(str(int(d1[1])+i))
	else:
		opn[int(d1[1])+i-12] = 0
		clo[int(d1[1])+i-12] = 0
		mon.append(str(int(d1[1])+i-12))
print(opn)
print(clo)
print(mon)
for issues in repo.fetch():
    # Create the object (dictionary) to upload to ElasticSearch
	# Create the object (dictionary) to upload to ElasticSearch
	if(i==90):
		break
	if 'pull_request' in issues['data']:
		continue
	else:
		if(issues['data']['state'] == 'closed'):
			if(isrecent(issues['data']['created_at'],d1,clo)):
				print("Issues ",i, " closed") 	
				print(issues['data']['created_at'])
				closed+=1
		else:
			if(isrecent(issues['data']['created_at'],d1,opn)):
				print("Issues",i," open")
				open1+=1
		
	#print(summary)'''
	#summary = {'hash':issues['data']}
	#print({'hash':issues['data']['state']})
	#es.index(index='issues', doc_type='summary', body=summary)
	# Upload the object to ElasticSearch
	#print(commit)
	i+=1
	print(".")
	#break
closed-=1
open1-=1
print("Closed: ", closed)
print("Open: ", open1)
#print(clo)
op = []
cl = []
for i in mon:
	op.append(opn[int(i)])
for i in mon:
	cl.append(clo[int(i)])
print(op)
print(cl)
print(mon)
#print(opn)
fig = plt.figure()
plt.plot(mon,op,'r-',label='Open')
plt.plot(mon,cl,'b-',label='Closed')
fig.suptitle('Time-to-close', fontsize=20)
plt.xlabel('Month', fontsize=18)
plt.ylabel('Amount', fontsize=16)
fig.savefig('test.png')
plt.show()


