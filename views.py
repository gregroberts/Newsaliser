from flask import Flask, request, Response, abort, render_template
from flask.ext.classy import FlaskView, route
from json import dumps
import stats, models
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
		heads, results = models.get_articles()
		return render_template(
			'articles.html',
			heads= heads,
			results=results,
			searchUrl='articles/search'
			)		


	def get(self, id):
		article = models.get_full_article(id=id)
		return render_template(
			'article.html',
			**article
			)

	def search(self, query):
		results = models.search_nodes('Article','n.title',query)
		return render_template(
			'articles.html',
			articles=results
			)

class TopicsView(FlaskView):
	def index(self):
		topics = models.get_topics()
		return render_template(
			'topics.html',
			topics=topics
			)

	def get(self, id):
		topic = models.get_full_topic(id)
		return render_template(
			'topic.html',
			**topic
			)

	def search(self, query):
		results = models.search_nodes('Topic','n.name',query)
		return render_template(
			'topics.html',
			topics=results
			)

class DomainsView(FlaskView):
	def index(self):
		heads, results = models.get_domains()
		return render_template(
			'domains.html',
			heads= heads,
			results=results,
			)

	def get(self, id):
		try:
			domain = models.get_full_domain(id=id)
		except ValueError:
			domain = models.get_full_domain(domain=id)
		return render_template(
			'domain.html',
			**domain
			)


app = Flask(__name__)
ArticlesView.register(app)
TopicsView.register(app)
DomainsView.register(app)

app.config['REDIS_HOST'] = models.REDIS_HOST
app.config['REDIS_PORT'] = models.REDIS_PORT
app.config['REDIS_PASSWORD'] = models.REDIS_PW
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