from db import *
import stats

def get_articles(limit = 100, order = 'n.title'):
    arts = get_nodes('Article', limit, order=order)
    #heads = arts[0].keys() if len(arts)>0 else []
    heads = ['title','date','author','domain','time', 'id',]
    get_vals = lambda x: map(lambda i: x[i], heads)
    results = map(lambda x: get_vals(x), arts)
    for arti, i in zip(arts, results):
        link = '<a href="/articles/%d">' % arti.id
        link += i[heads.index('title')] + '</a>'
        domain_link = '<a href="/domains/%s">' % i[heads.index('domain')]
        domain_link += i[heads.index('domain')] + '</a>'
        i[heads.index('title')] = link
        i[heads.index('domain')] = domain_link
    return heads, results

def get_article_pg(id = None, url = None): 
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

def get_full_article(id=None, url=None):
        art = dict(get_node(int(id)).items())
        res = get_article_pg(id, url)
        if res != None:
            art['text'] = res[2].decode('ascii',errors='ignore')
            art['html'] = res[3].decode('ascii',errors='ignore')
        else:
            art['text'] = art['html'] = ''
        sources = get_article_sources(art['url'])
        citations = get_article_citations(art['url'])
        topics = get_article_topics(art['url'])        
        article = dict(
            sources=sources,
            citations = citations,
            nCitations=len(citations),
            nSources=len(sources),
            topics=topics,
            **art
            )
        return article

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

def get_domains(limit = 1000, order = 'n.articles'):
    doms = get_nodes('Domain', limit, order=order)
    heads = ['domain','articles']
    get_vals = lambda x: map(lambda i: x[i], heads)
    results = map(lambda x: get_vals(x), doms) 
    return heads, results

def get_full_domain(id = None, domain=None):
    if id is not None:
        domain = dict(get_node(id).items())
    else:
        domain = dict(get_node_by_propval('domain',domain))
    articles = get_domain_articles(domain['domain'])
    statistics = stats.get_domain_stats(domain=domain['domain'])
    nArticles, citedDomain, citingDomain = statistics
    domain['articles'] = articles
    return dict(
        sources=citedDomain, 
        citers=citingDomain,
        nArticles=nArticles,
        **domain
        )

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

def get_topics(order='n.name',limit = 100):
    topics = get_nodes('Topic',order=order,limit=limit)
    return topics

def get_full_topic(id):
    topic = get_node(id)
    articles = get_topic_articles(topic['name'])
    return dict(
        articles=articles,
        **topic
        )