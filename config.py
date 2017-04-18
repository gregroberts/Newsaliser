import os
import urlparse


try:
	from local_config import *
except:

	NEO4J_URL = os.environ['GRAPHENEDB_BOLT_URL']
	NEO4J_USER= os.environ['GRAPHENEDB_BOLT_USER']
	NEO4J_PW= os.environ['GRAPHENEDB_BOLT_PASSWORD']

	url = urlparse.urlparse(os.environ['DATABASE_URL'])
	POSTGRES_DB = url.path[1:]
	POSTGRES_USER = url.username
	POSTGRES_PW = url.password
	POSTGRES_URL = url.hostname
	POSTGRES_PORT = url.port

	url = urlparse.urlparse(os.environ['REDISTOGO_URL'])
	REDIS_HOST= url.hostname
	REDIS_PORT= url.port