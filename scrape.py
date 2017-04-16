from neo import session
import newspaper

def consume_article(url, author, date, text,title,  links):
    session.run('''
        MERGE (n:Article {url:{url}})
        SET
            n.title={title},
            n.author={author},
            n.date={date},
            n.text={text}
    ''', {
        'title':title,
        'url':url,
        'author':author,
        'date':date,
        'text':text,
    }).consume()
    for link in links:
        session.run('''
            MATCH (n:Article {url:{url}})
            MERGE (m:Article {url:{lurl}})
            with n,m
            MERGE (n)-[:CITES {text:{text}}]->(m)
        ''', {
            'url':url,
            'lurl':link['url'],
            'text':link['text']
        }).consume()

def parse_article(url):
    a = newspaper.Article(url)
    a.download()
    a.parse()
    try:
        date=a.publish_date.strftime('%Y-%m-%d')
    except:
        date = 'Unknown'
    return {
        'url':url,
        'author':','.join(a.authors),
        'date':date,
        'text':a.text,
        'title':a.title,
        'links':[{'url':''.join(x.xpath('./@href')),'text':''.join(x.xpath('./text()'))} for x in a.clean_top_node.xpath('//a')]
    }

def merge_article(article):
    print article
    if type(article) is list:
    	article = article[0]
    data = parse_article(article)
    if data != None:
        consume_article(
            article,
            data['author'],
            data['date'],
            data['text'],
            data['title'],
            data['links']
        )