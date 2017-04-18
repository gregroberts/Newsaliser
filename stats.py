from db import session

def get_domain_topics(domain):
	return list(session.run('''
		MATCH (n:Domain {domain:{domain}})
		match (n)<-[:FROM]-(a)-[:MENTIONS]->(t:Topic)
		return t.name as topic, count(distinct a) as articles
		order by articles desc
		''', {'domain':domain}))

def get_domain_sources(domain, limit =20):
	return list(session.run('''
		MATCH (n:Domain {domain:{domain}})
		match (n)<-[:FROM]-(a)-[:CITES]->()-[:FROM]->(m:Domain)
		return m.domain as citedDomain, count(distinct a) as articles, id(m) as id
		order by articles desc limit {limit}
		''', {'domain':domain, 'limit':limit}))

def get_domain_citers(domain, limit =20):
	return list(session.run('''
		MATCH (n:Domain {domain:{domain}})
		match (n)<-[:FROM]-(a)<-[:CITES]-()-[:FROM]->(m:Domain)
		return m.domain as citingDomain, count(distinct a) as articles, id(m) as id
		order by articles desc limit {limit}
		''', {'domain':domain, 'limit':limit}))

