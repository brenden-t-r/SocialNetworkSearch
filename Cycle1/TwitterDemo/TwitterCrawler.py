import twitter
from BasicSearch import BasicSearch

class TwitterCrawler(object):

	# Login to api
	def login(self):
		self.api = twitter.Api(consumer_key='684nljJUHfn6SCaYSCG0yAhbW',
						consumer_secret='mIRCyxLdIC5cQc7HukUtb7KhKqIvSYOB6LjBZb3CQOQ2n4ents',
						access_token_key='2805813624-2V4XKmbtM18s8osRDpSsr4H2An7JTpMdBE5N2la',
						access_token_secret='szChpRZhXg9F7n5gmlQhG2gEXe5C5g1vgYLGfqmeViPj8'
						)
		return self.api
	
	# Search
	def BasicSearch(self, db, scorer, query, args):
		search = BasicSearch(self.api, db, scorer, query, args)
		return search.search()
