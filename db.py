from neo4j.v1 import GraphDatabase, basic_auth
from config import *
from operator import itemgetter
import psycopg2
from rq import Queue
import redis

pool = redis.ConnectionPool(
        host = REDIS_HOST,
        port = REDIS_PORT,
        password = REDIS_PW
)
def get_rc():
    redis_conn = redis.StrictRedis(
            connection_pool=pool,
            decode_responses=True
    )
    return redis_conn

def get_pgconn():
    return psycopg2.connect(host=POSTGRES_URL,port=POSTGRES_PORT,
                          user=POSTGRES_USER,
                 password=POSTGRES_PW,
                 database=POSTGRES_DB)

driver = GraphDatabase.driver(
    NEO4J_URL, 
    auth=basic_auth(NEO4J_USER, NEO4J_PW)
)

class session:
    @staticmethod
    def run(sttmnt, params):
        #print sttmnt
        sesh = driver.session()
        res = sesh.run(sttmnt, params)
        sesh.close()
        return res
    



def insert_article(id, url, html, text, raw_html):
    conn = get_pgconn()
    c=conn.cursor()
    c.execute('''
    INSERT INTO 
        articles
        (id,url,html, text, raw_html)
    VALUES
        (%s,%s,%s,%s, %s)
    ON CONFLICT (id) DO UPDATE
        SET html = EXCLUDED.html,
            text = EXCLUDED.text
    ;
    ''', (id,url,html,text, raw_html))
    c.close()
    conn.commit()
    conn.close()

def get_node(_id):
	return list(session.run('''
	MATCH (n)
	WHERE id(n) = {nid}
	return n
	''', {'nid':int(_id)}))[0]['n']

def get_node_by_propval(prop, val):
    return list(session.run('''
    MATCH (n)
    WHERE n.%s = {nid}
    return n
    ''' % prop, {'nid':val}))[0]['n']

def get_nodes(_type, limit = 10, order = 'n.time',
            returnmap={},
            filtermap=[]):
    to_return = ', '.join( 
        map(
            lambda x: '%s as %s' % x,
            returnmap.items()
        )
    ) or 'n'
    to_filter = 'and '.join(map(
            lambda x: ' '.join(x),
            filtermap
        )
    )
    if to_filter != '':
        to_filter = ' and ' + to_filter
    return map(itemgetter('n'),session.run('''
        MATCH (n:%s)
        where exists(%s)
         and %s <> 'Unknown'
         %s
        return %s
        order by %s desc
        limit {limit}
        ''' %( _type, order, order, to_filter, to_return, order), {'limit':limit}))

def search_nodes(_type, field, term, limit = 100, order = 'n.date'):
    regx="'(?i).*"+term+".*'"
    return get_nodes(
        _type,
        limit, order, 
        filtermap=[
            ('n.%s' % field, '=~', regx),
            ]
        )

def rq_add_job(func, kwargs, queue = 'default'):
    q = Queue(name = queue, connection = get_rc())
    j = q.enqueue(func, kwargs=kwargs, result_ttl=20)
    return j

if __name__ == '__main__':
    pgconn = get_pgconn()
    c = pgconn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS
            articles
            (
                id INT,
                url TEXT,
                text TEXT,
                html TEXT,
                raw_html TEXT,
                CONSTRAINT pkid PRIMARY KEY (id)
            )
    ''')
    pgconn.commit()

