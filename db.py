from neo4j.v1 import GraphDatabase, basic_auth
from config import *
from operator import itemgetter
import psycopg2
from rq import Queue
from redis import StrictRedis


def get_rc():
    redis_conn = StrictRedis(
            host = REDIS_HOST,
            port = REDIS_PORT,
    )
    return redis_conn

driver = GraphDatabase.driver(
    NEO4J_URL, 
    auth=basic_auth(NEO4J_USER, NEO4J_PW)
)

class session:
    @staticmethod
    def run(sttmnt, params):
        sesh = driver.session() 
        return sesh.run(sttmnt, params)
    

def get_pgconn():
    return psycopg2.connect(host=POSTGRES_URL,port=POSTGRES_PORT,
                          user=POSTGRES_USER,
                 password=POSTGRES_PW,
                 database=POSTGRES_DB)

def insert_article(id, url, html, text):
    conn = get_pgconn()
    c=conn.cursor()
    c.execute('''
    INSERT INTO 
        articles
        (id,url,html, text)
    VALUES
        (%s,%s,%s,%s)
    ;
    ''', (id,url,html,text))
    c.close()
    conn.commit()
    conn.close()

def update_article(id, url, html, text):
    conn = get_pgconn()
    c=conn.cursor()
    c.execute('''
    UPDATE
        articles
    SET
        url=%s,
        html=%s,
        text=%s
    WHERE 
        id=%s
    ;
    ''', (url,html,text, id))
    c.close()
    conn.commit()
    conn.close()

def get_article(id = None, url = None): 
    if id:
        val, prop = id, 'id'
    elif url:
        val, prop = url, 'url'
    else:
        return []
    conn = get_pgconn()
    c=conn.cursor() 
    sttmnt = '''
        SELECT 
            id,url,text, html
        from 
            articles
        where '''+prop+''' = %s
        ;
    ''' 
    c.execute(sttmnt, [val] )
    res = c.fetchone()
    c.close()
    conn.close()
    return res

def get_article_text(id=None, url=None):
    try:
        res = get_article(id, url)
        return res[2].decode('ascii',errors='ignore')
    except Exception as e:
        print e
        return ''

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

def get_nodes(_type, limit = 10, order = 'time'):
    return map(itemgetter('n'),session.run('''
        MATCH (n:%s)
        where exists(n.%s)
         and n.%s <> 'Unknown'
        return n 
        order by n.%s desc
        limit {limit}
        ''' %( _type, order, order, order), {'limit':limit}))

def search_nodes(_type, field, term, limit = 100, order = 'date'):
    regx='(?i).*'+term+'.*'
    return map(itemgetter('n'),session.run('''
        MATCH (n:%s)
        where n.%s =~ '%s'
        return n 
        order by n.%s desc
        limit {limit}
        ''' %( _type, field,regx, order), {'limit':limit}))

def get_article_sources(url):
    return list(session.run('''
        MATCH (n:Article {url:{url}})-[r:CITES]->(a:Article)
        return distinct
        	r.text as citeText, 
        	a.title as title,
            a.url as url,
            id(a) as id,
            a.date as date,
            a.author as author,
            a.domain as domain
        ''', {'url':url}))

def get_article_citations(url):
    return list(session.run('''
        MATCH (n:Article {url:{url}})<-[r:CITES]-(a:Article)
        return distinct
            r.text as citeText, 
            a.title as title,
            a.url as url,
            id(a) as id,
            a.date as date,
            a.author as author,
            a.domain as domain
        ''', {'url':url}))


def get_article_topics(url):
    return list(session.run('''
        MATCH (n:Article {url:{url}})-[r:MENTIONS]->(a)
        return 
            toInt(r.score) as score, 
            a.name as name,
            id(a) as id
        order by score desc
        ''', {'url':url}))

def get_topic_articles(name):
    return list(session.run('''
        MATCH (n:Topic {name:{name}})<-[r:MENTIONS]-(a)
        return 
            toInt(r.score) as score, 
            a.title as title,
            a.date as date,
            a.domain as domain,
            a.author as author,
            id(a) as id
        order by score desc, a.time desc
        ''', {'name':name}))   

def get_domain_articles(domain):
    return list(session.run('''
        MATCH (n:Domain {domain:{domain}})<-[r:FROM]-(a:Article)
        where exists(a.title)
        return 
            a.title as title,
            a.date as date,
            a.domain as domain,
            a.author as author,
            id(a) as id
        order by  a.time desc
        ''', {'domain':domain})) 

def rq_add_job(func, kwargs, queue = 'default'):
    q = Queue(name = queue, connection = get_rc())
    kwargs = {i: j.encode('ascii',errors='ignore') for i, j in kwargs.items()}
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
                html TEXT
            )
    ''')
    pgconn.commit()

