Commands:

*Assuming you used docker to use Elastic Search (docker run -d -p 9200:9200 -p 5601:5601 nshou/elasticsearch-kibana)
1)  p2o.py --enrich --index git_raw --index-enrich git \
    -e http://localhost:9200 --no_inc --debug \
    git https://github.com/grimoirelab/perceval.git
    
2) python perceval_elasticsearch_4_perceval.py

3) python pandas_1.py
