from flask import Flask, request, Response, abort, render_template
from flask.ext.classy import FlaskView, route
from json import dumps
import neo
from scrape import merge_article


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
		arts = neo.get_nodes('Article', 10)
		return render_template(
			'articles.html',
			articles=arts
			)

	def get(self, id):
		art = neo.get_node(id)
		sources = neo.get_article_sources(art['url'])
		topics = neo.get_article_topics(art['url'])
		return render_template(
			'article.html',
			sources=sources,
			nSources=len(sources),
			topics=topics,
			**art
			)



class TopicsView(FlaskView):
	def index(self):
		topics = neo.get_nodes('Topic',order='name',limit=10)
		return render_template(
			'topics.html',
			topics=topics
			)

	def get(self, id):
		topic = neo.get_node(id)
		articles = neo.get_topic_articles(topic['name'])
		return render_template(
			'topic.html',
			articles=articles,
			**topic
			)

class DomainsView(FlaskView):
	def index(self):
		domains = neo.get_nodes('Domain',order='articles',  limit=100)
		return render_template(
			'domains.html',
			domains=domains
			)

	def get(self, id):
		try:
			domain = dict(neo.get_node(id).items())
		except ValueError:
			domain = dict(neo.get_node_by_propval('domain',id.capitalize()))
		articles = neo.get_domain_articles(domain['domain'])
		domain['nArticles'] = len(articles)
		domain['articles'] = articles
		return render_template(
			'domain.html',
			**domain
			)


app = Flask(__name__)
ArticlesView.register(app)
TopicsView.register(app)
DomainsView.register(app)

@app.errorhandler(500)
def internal_error(e):
	print e
	return Response(
		response =dumps({'error':str(e)}),
		status = 500,
		mimetype = 'application/json'
	)

if __name__ == '__main__':
	def internal_error(e):
		print e
		return Response(
			response =dumps({'error':str(e)}),
			status = 500,
			mimetype = 'application/json'
		)
	app.run(host='0.0.0.0', debug=True)