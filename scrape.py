from tqdm import tqdm
import dateparser
from urlparse import urlparse,urljoin
from db import *
from models import get_article_pg
from topics import get_nounphrases
import goose, newspaper
from lxml.etree import tostring

 
def get_domain(url, indomain = None):
    if indomain != None:
        url = urljoin(indomain, url)
    return urlparse(url).netloc

def consume_source(url, link):
    domain = get_domain(link['url'],url)
    session.run('''
        MATCH (n:Article {url:{url}})
        MERGE (m:Article {url:{lurl}})
        ON CREATE SET m.domain={domain}
        WITH n,m
        MERGE (n)-[:CITES {text:{text}}]->(m)
        WITH m
        MATCH (d:Domain {name:{domain}})
        MERGE (m)-[:FROM]->(d)
    ''', {
        'url':url,
        'lurl':link['url'],
        'text':link['text'],
        'domain':domain
    }).consume()
    
def consume_topic(url, topic):
    session.run('''
        MATCH (n:Article {url:{url}})
        MERGE (m:Topic {name:{topic}})
        CREATE UNIQUE
            (n)-[:MENTIONS {score:{score}}]->(m)
    ''',{'url':url,'topic':topic[0],'score':topic[1]})   
    
def consume_article(**kwargs):
    topics = kwargs.pop('topics',[])
    links = kwargs.pop('links',[])
    id=list(session.run('''
        MERGE (n:Article {url:$map.url})
        SET
            n += $map
        with n
        merge (m:Domain {domain:$map.domain})
        MERGE (n)-[:FROM]->(m)
        return id(n)
    ''',{'map':kwargs}))[0]['id(n)']
    for link in links:
        if link['url'].startswith('http') and not link['url'].endswith('.pdf'):
            consume_source(kwargs['url'], link)
    for topic in topics:
        consume_topic(kwargs['url'], topic)
    return id

def parse_text(text):
    return get_nounphrases(text)


def parse_article(url):
    g = goose.Goose()
    a = g.extract(url) 
    return {
        'url':url,
        'author':','.join(a.authors),
        'date':str(dateparser.parse(a.publish_date or '')),
        'text':a.cleaned_text.replace('. ','.\n '),
        'title':a.title,
        'links':a.links,
        'topics':parse_text(a.cleaned_text),
        'html':tostring(a.doc),
        'domain':get_domain(url),
        'raw_html':a.raw_html
    }

def crawl_article_sources(links, crawl_depth = 0):
        if crawl_depth <MAX_CRAWL_DEPTH: 
            for i in set(links):
                rq_add_job(
                    func = merge_article,
                    kwargs = {
                        'article':i,
                        'crawl_depth':crawl_depth + 1
                    },
                    queue='default'
                ) 

def merge_article(article, crawl_depth=0):
    if type(article) is list:
        article = article[0]
    data = parse_article(article)
    text = data.pop('text')
    html = data.pop('html')
    raw_html = data.pop('raw_html')
    if data != None:
        id =  consume_article(
            **data
        )
        insert_article(id, article, html, text, raw_html)                
        links = filter(lambda x: x, map(
            lambda x: urljoin(article, x['url']
                            ).decode('ascii',errors='ignore').split('#')[0], 
            data['links']))
        crawl_article_sources(links, crawl_depth)
        return id
    else:
        raise Exception('Failed to merge article')

def merge_domain(domain):
    if not 'http:' in domain:
        domain = 'http://' + domain
    paper = newspaper.build(domain)
    articles = map(lambda x: x.url, filter(lambda x: paper.url in x.url, paper.articles))
    print 'Consuming %d Articles' % len(articles)
    for ind, article in enumerate(articles):
        print 'Article ',ind, ' - ',paper.url
        try:
            merge_article(article)
        except Exception as e:
            print e

