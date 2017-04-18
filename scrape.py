import dateparser
from urlparse import urlparse,urljoin
from db import *
from rake import rake
import sys
sys.path.insert(0,'C:\Users\Gerg\Documents\GitHub\python-goose')
import goose



def get_domain(url, indomain = None):
    if indomain != None:
        url = urljoin(indomain, url)
    x = '.'.join(url.replace('www','x').split('.')[:-1])
    return sorted(
            urlparse(x).netloc.split('.'),
            key=len,
            reverse=True
        )[0].capitalize()

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
    rq_add_job(
        func = merge_article,
        kwargs = {'article':link['url']},
        queue='default'
    )
    
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
    return filter(
            lambda x: x[1] > 1,
            [(i[0], int(i[1])) for i in rake.rake(text)]
        )


def scrape_article(url):
    article = get_article(url=url)
    g = goose.Goose()
    if bool(article)==False:
        print 'url',url
        article = g.extract(url)
        new = True
    else:
        article = g.extract(raw_html=article[3])
        new = False
        print 'hit!'
    return article, new



def parse_article(url):
    print url
    a, new = scrape_article(url)
    authors = ','.join(a.authors)
    date = dateparser.parse(a.publish_date or '')
    title= a.title
    text = a.cleaned_text
    html = a.raw_html
    domain = get_domain(url)
    links = a.links
    topics = parse_text(text)
    return {
        'url':url,
        'author':authors,
        'date':str(date),
        'text':text.replace('. ','.\n '),
        'title':title,
        'links':links,
        'topics':topics,
        'html':html,
        'domain':domain
    }, new

def merge_article(article):
    if type(article) is list:
        article = article[0]
    data, new = parse_article(article)
    text = data.pop('text')
    html = data.pop('html')
    if data != None:
        id =  consume_article(
            **data
        )
        if new:
            insert_article(id, article, html, text)
        else:
            update_article(id, article, html, text)
        return id
    else:
        raise Exception('Failed to merge article')