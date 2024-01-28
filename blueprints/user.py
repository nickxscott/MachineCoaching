from flask_login import UserMixin
import pandas as pd

#db connection imports
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv('pg.env')

"""
The class that you use to represent users needs to implement these properties and methods:

is_authenticated
This property should return True if the user is authenticated, i.e. they have provided valid credentials. 
(Only authenticated users will fulfill the criteria of login_required.)

is_active
This property should return True if this is an active user - in addition to being authenticated, 
they also have activated their account, not been suspended, or any condition your application has for rejecting an account. Inactive accoun>

is_anonymous
This property should return True if this is an anonymous user. (Actual users should return False instead.)

get_id()
This method must return a str that uniquely identifies this user, and can be used to load the user from the user_loader callback. Note that this must be a str - if the ID is natively an int or some other type, you will need to convert i>

To make implementing a user class easier, you can inherit from UserMixin,
"""

# Simulate user database
USERS_DB = {}


class User(UserMixin):

    """Custom User class."""
    def __init__(self, user_id, first, last, email):
        self.id = user_id
        self.first = first
        self.last = last
        self.email = email

    #I dont think I need any of these since I'm using postgres db
    #def claims(self):
    #    """Use this method to render all assigned claims on profile page."""
    #    return {'name': self.name,
    #            'email': self.email}.items()

    @staticmethod
    def get(user_id):
        conn = psycopg2.connect(host=os.getenv('ENDPOINT'), 
                            port=os.getenv('PORT'), 
                            database=os.getenv('DBNAME'), 
                            user=os.getenv('USER'), 
                            password=os.getenv('PWD'))
        cur = conn.cursor()
        cur.execute("SELECT * \
                    FROM USERS \
                        WHERE USER_ID = \'" + user_id + "'")
        query_results = cur.fetchall()
        col_nms=[x.name for x in cur.description]
        df=pd.DataFrame(query_results)
        df.columns=col_nms
        return User(user_id=df.user_id.values[0], first=df.first_name.values[0], last=df.last_name.values[0], email=df.email.values[0])

    #@staticmethod
    #def create(user_id, name, email):
    #    USERS_DB[user_id] = User(user_id, name, email)