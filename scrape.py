import newspaper
from urlparse import urlparse,urljoin
from neo import session
from rake import rake

def get_domain(url, indomain = None):
    if indomain != None:
        url = urljoin(indomain, url)
    x = '.'.join(url.replace('www','x').split('.')[:-1])
    return sorted(
    		urlparse(x).netloc.split('.'),
	    	key=len,
	    	reverse=True
    	)[0].capitalize()

def consume_article(url, author, date, text,title,  links, topics):
    domain = get_domain(url)
    session.run('''
        MERGE (n:Article {url:{url}})
        SET
            n.title={title},
            n.author={author},
            n.date={date},
            n.text={text},
            n.domain={domain}
    ''', {
        'title':title,
        'url':url,
        'author':author,
        'date':date,
        'text':text,
        'domain':domain
    }).consume()
    for link in links:
    	domain = get_domain(link['url'],url)
        session.run('''
            MATCH (n:Article {url:{url}})
            MERGE (m:Article {url:{lurl}})
            ON CREATE SET m.domain={domain}
            with n,m
            MERGE (n)-[:CITES {text:{text}}]->(m)
            with m
            MATCH (d:Domain {name:{domain}})
            merge (m)-[:FROM]->(d)
        ''', {
            'url':url,
            'lurl':link['url'],
            'text':link['text'],
            'domain':domain
        }).consume()
    for topic in topics:
    	session.run('''
	        MATCH (n:Article {url:{url}})
	        MERGE (m:Topic {name:{topic}})
	        CREATE UNIQUE
	            (n)-[:MENTIONS {score:{score}}]->(m)
	    ''',{'url':url,'topic':topic[0],'score':topic[1]})

    return list(session.run('''
            MATCH (n:Article {url:{url}})
            return id(n)
        ''', {
            'url':url,
        }))[0]['id(n)']

def parse_text(text):
	return rake.rake(text)

def parse_article(url):
    a = newspaper.Article(url)
    a.download()
    a.parse()
    try:
        date=a.publish_date.strftime('%Y-%m-%d')
    except:
        date = 'Unknown'
    topics = parse_text(a.text)
    return {
        'url':url,
        'author':','.join(a.authors),
        'date':date,
        'text':a.text,
        'title':a.title,
        'links':[{'url':''.join(x.xpath('./@href')),'text':''.join(x.xpath('./text()'))} for x in a.clean_top_node.xpath('//a')],
        'topics':topics
    }

def merge_article(article):
    print article
    if type(article) is list:
    	article = article[0]
    data = parse_article(article)
    if data != None:
        return consume_article(
            **data
        )
    else:
    	raise Exception('Failed to merge article')