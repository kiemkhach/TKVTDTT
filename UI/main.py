from flask import Flask, escape, request, render_template
import pysolr
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/search')
def search():
    arg = parse_param(request.args)
    if len(arg) > 0:
        print(arg)
        result = solr.search('*:*', fq=arg, **{
            'hl': 'true',
            'hl.fragsize': 50,
        })
    else:
        result = solr.search('*:*', **{
            'hl': 'true',
            'hl.fragsize': 50,
        })
    rows = getResult(result)
    return { "total": len(rows), "totalNotFiltered": len(rows), "rows":rows }
    
def parse_param(inputs):
    arg = ['%s:*%s*' % (key, inputs.get(key)) for key in inputs.to_dict() if (key not in ['', 'from_date', 'to_date', 'queryParams'])]
    from_date = inputs.get('from_date')
    to_date = inputs.get('to_date')
    if(from_date and to_date and (from_date + to_date != '')):
        arg.append('created:[%s TO %s]' % (from_date if from_date != '' else '*', to_date if to_date != '' else '*') )
    return arg
    
def connect():
    pysolr.ZooKeeper.CLUSTER_STATE = '/collections/viblo_posts/state.json'
    zookeeper = pysolr.ZooKeeper("localhost:9983")
    solr = pysolr.SolrCloud(zookeeper, 'viblo_posts')
    return solr
    
def getResult(result):
    i = 0
    rows = []
    for item in result:
        json_item = {}
        json_item['url'] = item['id']
        json_item['id'] = i
        json_item['author'] = item['author']
        json_item['created'] = item['created']
        json_item['title'] = item['title']
        rows.append(json_item)
        i += 1
    return rows
    
if __name__ == '__main__':
    solr = connect()
    app.run(debug=True)