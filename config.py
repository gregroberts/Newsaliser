impost os

try:
	from local_config import *
except:

	NEO4J_URL  os.environ.get("NEO4J_URL","")
	NEO4J_USER= os.environ.get("NEO4J_USER","")
	NEO4J_PW= os.environ.get("NEO4J_PW","")

	POSTGRES_URL= os.environ.get("POSTGRES_URL","")
	POSTGRES_PORT= os.environ.get("POSTGRES_PORT","")
	POSTGRES_USER= os.environ.get("POSTGRES_USER","")
	POSTGRES_PW= os.environ.get("POSTGRES_PW","")
	POSTGRES_DB= os.environ.get("POSTGRES_DB","")

	REDIS_HOST= os.environ.get("REDIS_HOST","")
	REDIS_PORT= os.environ.get("REDIS_PORT","")