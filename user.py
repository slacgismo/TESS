import json
class user:

	def __init__(self,database,request,**kwargs):
		"""Construct a user object
		
		Parameters:
			database <mysql.tess> 	database object
			request					operation request ('get','check','create')
			name <str> 				user name
			password <str> 			user password (default no password)
			use_throw <boolean>		use throw for error (default false)
			user(database,name,use_throw)

		Return: <user> object
		"""
		self.database = database
		use_throw = "use_throw" in kwargs and kwargs["use_throw"]
		if request == 'get':
			self.get(**kwargs)
			self.is_valid = True
		elif request == 'check':
			self.check(**kwargs)
			self.is_valid = True
		elif request == 'create':
			self.create(**kwargs)
			self.is_valid = True
		elif request == 'delete':
			self.delete(**kwargs)
			self.is_valid = True
		elif request == 'change':
			self.change(**kwargs)
			self.is_valid = True
		elif use_throw:
			raise Exception("invalid request")
		else:
			self.is_valid = False

	def to_dict(self):
		"""Convert from <user> object to <dict>"""
		result = {}
		for key,value in self.__dict__.items():
			if type(value) in [int,str,float]:
				result[key] = value
		return result

	def from_dict(self,data):
		"""Convert from <user> object to <dict>"""
		if data:
			for arg,value in data.items():
				setattr(self,arg,value)

	def get(self,**kwargs):
		use_throw = "use_throw" in kwargs and kwargs["use_throw"]
		if "name" in kwargs :
			self.name = kwargs["name"]
			self.user_id = self.database.find_user(
				name = self.name,
				use_throw = use_throw)
		self.from_dict(self.database.get_user(
			user_id = self.user_id,
			use_throw = use_throw))
		if self.sha1pwd == "DELETED":
			raise "user not found"
		else:
			return self.to_dict()

	def check(self,**kwargs):
		use_throw = "use_throw" in kwargs and kwargs["use_throw"]
		self.get(**kwargs)
		if "password" in kwargs:
			try:
				self.from_dict(self.database.get_user(
					user_id = self.user_id,
					password = kwargs["password"],
					use_throw=True))
				self.is_authenticated = True
			except:
				self.is_authenticated = False
			if use_throw and not self.is_authenticated:
				raise Exception("invalid password")
		else:
			self.from_dict(self.database.get_user(
				user_id = self.user_id,
				use_throw = use_throw))
			self.is_authenticated = False

	def create(self,**kwargs):
		use_throw = "use_throw" in kwargs and kwargs["use_throw"]
		try: 
			self.get(**kwargs,use_throw=True)
		except:
			self.user_id = self.database.add_user(**kwargs)
			self.get()
			return self.user_id
		raise Exception("user already exists")

	def delete(self,**kwargs):
		use_throw = "use_throw" in kwargs and kwargs["use_throw"]
		kwargs["sha1pwd"] = "DELETED"
		self.database.add_user(**kwargs)

	def change(self,**kwargs):
		print(kwargs)
		use_throw = "use_throw" in kwargs and kwargs["use_throw"]
		data = self.to_dict()
		print(data)
		del data["user_id"]
		for key,value in kwargs.items():
			if key in data.keys():
				data[key] = value
		print(data)
		self.database.add_user(**data)
