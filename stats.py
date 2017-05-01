from db import session

def get_domain_stats(domain):
	return map(lambda x: ( x['nArticles'], x['citedDomain'], x['citingDomain']), 
		session.run('''
		MATCH (n:Domain {domain:{domain}})
		with n
		match (n)<-[r:FROM]-()
		with n, count(distinct r) as nArticles
		match (n)<-[:FROM]-(a)-[:CITES]->()-[:FROM]->(m:Domain)
		with n, nArticles, [m.domain, count(distinct a), id(m)] as citedDomain
		with n, nArticles, collect(citedDomain) as citedDomain
		match (n)<-[:FROM]-(a)<-[:CITES]-()-[:FROM]->(m:Domain)
		with n, nArticles, citedDomain,[m.domain, count(distinct a), id(m)] as citingDomain
		with nArticles, citedDomain, collect(citingDomain) as citingDomain
		return *
		''', {'domain':domain}))[0]
