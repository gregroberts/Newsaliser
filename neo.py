from neo4j.v1 import GraphDatabase, basic_auth
from config import *
from operator import itemgetter


driver = GraphDatabase.driver(
    NEO4J_URL, 
    auth=basic_auth(NEO4J_USER, NEO4J_PW)
)
session = driver.session() 


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

def get_article_sources(url):
    return list(session.run('''
        MATCH (n:Article {url:{url}})-[r:CITES]->(a)
        optional match  ()-[inin:CITES]->(a)
        optional match  (a)-[out:CITES]->() 
        return 
        	r.text as citeText, 
        	a.title as title,
            a.url as url,
            id(a) as id,
            a.date as date,
            a.author as author,
            a.domain as domain,
        	count(distinct out) as cites,
        	count(distinct inin) as cited
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

if __name__ == '__main__':
    print get_nodes('Article')