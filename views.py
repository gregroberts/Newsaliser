from flask import Flask, request, Response, abort, render_template
from flask.ext.classy import FlaskView, route
from json import dumps
import db, stats
from scrape import merge_article
import rq_dashboard
from traceback import format_exc


class ArticlesView(FlaskView):
	def post(self):
		url = request.get_data()
		_id = merge_article(url)
		res ={
			'result':'Success',
			'id':_id
		}
		return Response(
				response = dumps(res),
				status = 200,
				mimetype= 'application/json'
			)

	def index(self):
		arts = db.get_nodes('Article', 1000, order='title')
		return render_template(
			'articles.html',
			articles=arts
			)

	def new(self):
		arts = db.get_nodes('Article', 12, order='title')
		#heads = arts[0].keys() if len(arts)>0 else []
		heads = ['title','date','author','domain','time']
		get_vals = lambda x: map(lambda i: x[i], heads)
		results = map(lambda x: get_vals(x), arts)
		return render_template(
			'new_articles.html',
			articles=arts,
			heads= heads,
			results=results,
			searchUrl='articles/search'
			)		


	def get(self, id):
		art = dict(db.get_node(id).items())
		sources = db.get_article_sources(art['url'])
		citations = db.get_article_citations(art['url'])
		topics = db.get_article_topics(art['url'])
		art['text'] = db.get_article_text(id=int(id))
		return render_template(
			'article.html',
			sources=sources,
			citations = citations,
			nCitations=len(citations),
			nSources=len(sources),
			topics=topics,
			**art
			)

	def search(self, query):
		results = db.search_nodes('Article','title',query)
		return render_template(
			'articles.html',
			articles=results
			)

class TopicsView(FlaskView):
	def index(self):
		topics = db.get_nodes('Topic',order='name',limit=10)
		return render_template(
			'topics.html',
			topics=topics
			)

	def get(self, id):
		topic = db.get_node(id)
		articles = db.get_topic_articles(topic['name'])
		return render_template(
			'topic.html',
			articles=articles,
			**topic
			)

	def search(self, query):
		results = db.search_nodes('Topic','name',query)
		return render_template(
			'topics.html',
			topics=results
			)

class DomainsView(FlaskView):
	def index(self):
		domains = db.get_nodes('Domain',order='domain',  limit=100)
		return render_template(
			'domains.html',
			domains=domains
			)

	def get(self, id):
		try:
			domain = dict(db.get_node(id).items())
		except ValueError:
			domain = dict(db.get_node_by_propval('domain',id.capitalize()))
		articles = db.get_domain_articles(domain['domain'])
		sources = stats.get_domain_sources(domain['domain'])
		citers = stats.get_domain_citers(domain['domain'])
		domain['nArticles'] = len(articles)
		domain['articles'] = articles
		return render_template(
			'domain.html',
			sources=sources,
			citers = citers,
			**domain
			)


app = Flask(__name__)
ArticlesView.register(app)
TopicsView.register(app)
DomainsView.register(app)

app.config['REDIS_HOST'] = db.REDIS_HOST
app.config['REDIS_PORT'] = db.REDIS_PORT
app.config['REDIS_PASSWORD'] = db.REDIS_PW
app.config['RQ_POLL_INTERVAL'] = 2000
app.config['APPLICATION_ROOT'] = '/'
app.register_blueprint(rq_dashboard.blueprint, url_prefix='/redis_queue')

@app.errorhandler(500)
def internal_error(e):
	print e
	return Response(
		response =dumps({'error':str(e),'traceback':format_exc()}),
		status = 500,
		mimetype = 'application/json'
	)

@app.route('/')
def index():
	return '<h1>Hello World</h1>'

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)