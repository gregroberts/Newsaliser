from db import *

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