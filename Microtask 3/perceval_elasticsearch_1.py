from perceval.backends.core.github import GitHub
from perceval.backends.core.git import Git
from datetime import date
import pandas as pd
from dateutil.relativedelta import relativedelta
from pprint import pprint

import elasticsearch



def isrecent(d1,day,month_num,year):
	if(date(int(d1[0]),int(d1[1]),int(d1[2])) < date(year,month_num,day)):
		return True
	return False

def repo_info(own,repo_url,d1,df,k):
	#repo_url = 'INFO1601'
	# Directory for letting Perceval clone the git repo
	#repo_dir = 'grimoirelab-perceval'
	token = -XXX
	#own = 'kmn5409'
	# ElasticSearch instance (url)
	#es = elasticsearch.Elasticsearch(['http://localhost:9200/'])
	#repo = 'grimoirelab-perceval'

	# Create the 'commits' index in ElasticSearch
	#es.indices.create('issues')
	# Create a Git object, pointing to repo_url, using repo_dir for cloning
	repo = GitHub(owner=own,repository=repo_url,api_token=token)
	# Fetch all commits as an iteratoir, and iterate it uploading to ElasticSearch
	pull_open = 0
	open1 = 0
	total = 0
	for issues in repo.fetch():
	    # Create the object (dictionary) to upload to ElasticSearch
		# Create the object (dictionary) to upload to ElasticSearch
		if 'pull_request' in issues['data']:
			if(issues['data']['state'] == 'open'):
				#print("Pull Request ",p,"open")s
				temp = issues['data']['created_at'].split("-")
				year = int(temp[0])
				month_num = int(temp[1])
				day = int(temp[2][:2])
				if(isrecent(d1,day,month_num,year)):
					pull_open+=1
		else:
			if(issues['data']['state'] == 'open'):
				temp = issues['data']['created_at'].split("-")
				year = int(temp[0])
				month_num = int(temp[1])
				day = int(temp[2][:2])
				if(isrecent(d1,day,month_num,year)):
					open1+=1
		#print(".")
		#print(summary)
		#summary = {'hash':issues['data']}
		#print({'hash':issues['data']['state']})
		#es.index(index='issues', doc_type='summary', body=summary)
		# Upload the object to ElasticSearch
		#print(commit)
		#break
	total+=pull_open+open1
	df['Issues Open'][k] = open1
	df['Pull Requests Open'][k] = pull_open
	print("Open Issues", open1)
	print("Pull Requests: ", pull_open)
	print()
	return total

def commit_counter(own,repo_url,d1,df,k):
	# url for the git repo to analyze
	#repo_url = 'https://github.com/kmn5409/INFO1601.git'
	print("Owner\t\tRepository")
	print(own,"\t",repo_url)
	repo_url = 'https://github.com/' + own + '/' + repo_url + '.git'
	# directory for letting Perceval clone the git repo
	repo_dir = '/tmp/' + repo_url + '.git'

	# create a Git object, pointing to repo_url, using repo_dir for cloning
	repo = Git(uri=repo_url, gitpath=repo_dir)
	count = 0
	# fetch all commits as an iteratoir, and iterate it printing each hash
	mon = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
	for commit in repo.fetch():
		temp = commit['data']['CommitDate'].split(" ")
		day = int(temp[2])
		month = temp[1]
		for i in range(len(mon)):
			if(month == mon[i]):
				month_num = i+1
		year = int(temp[4])
		if(isrecent(d1,day,month_num,year)):
			count+=1
	print("Number of commmits: ", count)
	df['Number of commits'][k] = count
	return count




def main():
	repos = [["INFO1601","kmn5409"],["grimoirelab-perceval","chaoss"],
		 ["grimoirelab-mordred","chaoss"],["grimoirelab-cereslib","chaoss"],
		 ["grimoirelab-elk","chaoss"],]
	#repo_url = 'grimoirelab-perceval'
	k=0
	date1 = date.today() + relativedelta(months=-3)
	date1 = str(date1)
	print(date1)
	d1 = date1.split("-")
	print("For the last three months")
	df = pd.DataFrame(columns=["Repository","Number of commits","Issues Open",
				   "Pull Requests Open","Total"])
	for i in repos:
		df.loc[k] = [0,0,0,0,0]
		total = 0
		df['Repository'][k] = 0
		df['Issues Open'][k] = 0
		df['Pull Requests Open'][k] = 0
		df['Total'][k] = 0
		df['Repository'][k] = repos[k][1]+ "\\" + repos[k][0]
		total+=commit_counter(i[1],i[0],d1,df,k)
		total+=repo_info(i[1],i[0],d1,df,k)
		print(total)
		df['Total'][k] = total
		k+=1
	print(df,"\n\n")
	df.sort_values(by='Total', ascending=True, inplace=True)
	df = df.reset_index(drop=True)
	print(df)
	df.to_csv('total.csv',index=False)

if __name__ == "__main__":
	main()
