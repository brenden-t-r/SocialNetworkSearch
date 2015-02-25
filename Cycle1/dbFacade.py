from cassandra.cluster import Cluster
import cassandra.cluster
import time
import uuid

'''
This class handles database communication and should
be used instead of interacting with the database directly.

@author: Brenden Romanowski
@date: 24 Feb 2015
'''

class dbFacade(object):
	session = None
	keyspace = None
	
	def connect(self):
		while(True):
			try:
				cluster = Cluster(['131.204.27.98'])
				self.session = cluster.connect()
				break;
			except cassandra.cluster.NoHostAvailable:
				print "Connection failed, retrying.."
				time.sleep(1)
			except Exception as e:
				print str(e)
				time.sleep(1)
		print "Connected to cassandra database."
		
	def close(self):
		time.sleep(1)
		self.session.cluster.shutdown()
		self.session.shutdown()
		
	def add_user(self, username, score, website):
		self.session.execute("""
			INSERT INTO %s.users (username, score, website)
			VALUES ('%s', %s, '%s'); 
			""" % (self.keyspace, username, score, website))
			
	def add_post(self, username, website, content, query, score):	
		self.session.execute("""
			INSERT INTO %s.posts (id, username, website, content, query,  score)
			VALUES (%s, '%s', '%s', '%s', '%s', %s);
			""" % (self.keyspace, uuid.uuid1(), username, website, content, query, score))
	
	def get_users(self):
		results = self.session.execute("""
				SELECT * FROM %s.users;
				""" % self.keyspace)
		return results
	
	def get_users_dict(self):
		self.session.row_factory = cassandra.query.dict_factory
		users = self.get_users()
		return users

	def get_scored_users(self):
		results = self.session.execute("""
				SELECT * FROM %s.scored_users LIMIT 10;
				""" % self.keyspace)
		return results

	def get_posts(self, username):
		results = self.session.execute("""
				SELECT * FROM %s.posts WHERE username='%s';
				""" % (self.keyspace, username))
		return results

	def insert_user_score(self, username, score, website):
		self.session.execute("""
				INSERT INTO %s.scored_users (username, score, website) 
				VALUES ('%s', %s, '%s');
				""" % (self.keyspace, username, int(score), website))
	
	'''
	This function should possibly be in Scorer instead of dbFacade
	'''
	def calculate_user_scores(self, users):
		scores = []

		for user in users:
			posts = self.get_posts(user['username'])
			for post in posts:
				user['score'] = user['score'] + post['score']
			scores.append(user['score'])

		return scores

	def populate_user_scores(self, users, scores):
		for i in range(0, len(users)):
			self.insert_user_score(
				users[i]['username'], 
				users[i]['score'], 
				users[i]['website'])
		
	def create_keyspace_and_schema(self):
		timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
		self.keyspace = "search_%s" % timestamp

		self.session.execute("""
			CREATE KEYSPACE %s WITH
			replication = {'class':'SimpleStrategy','replication_factor':3};
			""" % self.keyspace)
		
		self.session.execute("""
			CREATE TABLE %s.scored_users (
				username text,
				score int,
				website text,
				PRIMARY KEY (website, score, username)
			) WITH CLUSTERING ORDER BY (score DESC);
			""" % self.keyspace)

		self.session.execute("""
			CREATE TABLE %s.users (
				username text,
				website text,
				score int,
				PRIMARY KEY (username, website)
			);
			""" % self.keyspace)
		
		self.session.execute("""
			CREATE TABLE %s.posts (
				id uuid,
				username text,
				website text,
				content text,
				query text,
				score int,
				PRIMARY KEY (username, id)	
			);
			""" % self.keyspace)

	def clearDatabase(self):
		keyspaces = self.getKeyspaceNames()
		
		for keyspace in keyspaces:
			if "search" in keyspace:
				self.session.execute("""DROP KEYSPACE %s;""" % keyspace)
					
	def getKeyspaceNames(self):
		keys = self.session.execute("""
			SELECT * FROM system.schema_keyspaces;"""); 
			
		keyspaces = []
		for key in keys:
			keyspaces.append(key.keyspace_name)
			
		return keyspaces