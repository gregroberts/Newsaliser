from neo import session

def clean_all():
	list(session.run('''
	MATCH (n:Article)
	where
	    not(
	        n.url=~'^http.*'
	    )
	REMOVE n:Article
	SET n:DeadLink
	'''))

	list(session.run('''
	MATCH (n:Article)-[:FROM]->(a:Domain {domain:''})
	REMOVE n:Article
	SET n:DeadLink
	'''))

	list(session.run('''
	MATCH (n:Article)
	where
	    not(
	        n.url=~'^http.*'
	    )
	REMOVE n:Article
	SET n:DeadLink
	'''))

	list(session.run('''
	MATCH (n:Article)
	where n.domain in ['Twitter','Facebook']
	REMOVE n:Article
	SET n:SocialMedia
	'''))

	list(session.run('''
	MATCH (n:Article {domain:'Support'})
	REMOVE n:Article
	'''))


if __name__ == '__main__':
	clean_all()
