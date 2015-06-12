import settings
import requests
import json
from flask import Flask
import getpass
# https://answers.atlassian.com/questions/320093/asked-by-martin-hanke---unable-to-rename-a-jira-local-user-no-option

# used for logging purposes
app = Flask(__name__)

class JiraConnector(object):
    def __init__(self):
        self._url = settings.jira_url
        self._jsonheader = {'Content-Type':'application/json'}
        self._session = requests.Session()
        self._allgroup = 'jira-users'
        self._searchrange = 5000

        # url extensions
        self._ext = dict(
            session='/rest/auth/1/session',
            group='/rest/api/2/group',
            user_group='/rest/api/2/group/user',
            user='/rest/api/2/user',
            users='/rest/api/2/user/search',
            user_picker='/rest/api/2/user/picker',
            group_picker='/rest/api/2/groups/picker'
        )

    def login(self, usr, pwd):
        url = self._url + self._ext['session']
        payload = {
            'username':usr,
            'password':pwd
                   }
        self._session.auth = (usr, pwd)
        response = self._session.post(
            url,
            data=json.dumps(payload),
            headers=self._jsonheader
        )
        return response.status_code == 200, response.text

    def logout(self):  # what parameters will I have to pass in later?
        url = self._url + self._ext['session']
        response = self._session.delete(url)
        return response.status_code == 204, response.text

    # user CRUD operations

    def create_user(self, name, email, disp, pwd):
        url = self._url + self._ext['user']
        payload = {
            'name': name,
            'password': pwd,
            'emailAddress': email,
            'displayName': disp
        }
        response = self._session.post(
            url,
            data=json.dumps(payload),
            headers=self._jsonheader
        )
        return response.status_code == 201, response.text

    def get_user(self, username):
        url = self._url + self._ext['user']
        response = self._session.get(url,params={'username': username})
        return response.status_code == 200, response.text

    def update_user(self, name, email, username):
        url = self._url + self._ext['user']
        payload = {
            'name':name,
            'emailAddress':email,
            'displayName': disp
        }
        response = self._session.put(
            url,
            params={'username':username},
            data=json.dumps(payload),
            headers=self._jsonheader
        )
        return response.status_code == 200, response.text

    def delete_user(self, usrname):
        url = self._url + self._ext['user']
        response = self._session.delete(url,params={'username':usrname})
        return response.status_code == 204, response.text

    def search_user(self, query, exclude, page, limit):
        # ASSUMPTION: page numbers start at page 1 not 0
        url = self._url + self._ext['users']
        query_params = {
            'username': query,
            'exclude': exclude,
            'startAt': (page-1)*limit,
            'maxResults': limit
            # 'includeActive':false,
            # 'includeInactive':false
        }
        response = self._session.get(url,params=query_params)
        return response.status_code == 200, response.text

    def all_users(self, page, limit):
        url = self._url + self._ext['group']
        start = (page - 1) * limit
        end = page * limit - 1
        query_params = {
            'groupname':self._allgroup,
            'expand': ('users[%d:%d]' % (start, end))
        }
        response = self._session.get(url,params=query_params)
        return response.status_code == 200, response.text

    # group CRUD operations

    def create_group(self,grpname):
        url = self._url + self._ext['group']
        response = self._session.post(url,data=json.dumps({'name':grpname}),headers=self._jsonheader)
        return response.status_code == 201, response.text

    def get_group(self,grpname):
        url = self._url + self._ext['group']
        response = self._session.get(url,params={'groupname':grpname})
        return response.status_code == 200, response.text

    def add_user_group(self,username,grpname):
        url = self._url + self._ext['user_group']
        response = self._session.post(
            url,
            data=json.dumps({'name':username}),
            params={'groupname':grpname},
            headers=self._jsonheader,
        )
        return response.status_code == 201, response.text

    def delete_user_group(self, username, grpname):
        url = self._url + self._ext['user_group']
        response = self._session.delete(
            url,
            params={'groupname':grpname, 'username':username},
            headers=self._jsonheader,
        )
        return response.status_code == 200, response.text

    def delete_group(self,grpname):
        url = self._url + self._ext['group']
        response = self._session.delete(url,params={'groupname':grpname})
        return response.status_code == 200, response.text

    def search_group(self, query, exclude, page, limit):
        return self.page_group(query,exclude,page,limit)

    def page_group(self,query,exclude,page,limit):
        # temporarily store in an array of set size maybe like 5000?
        key = "g_%s" % query.lower()
        if key not in self._session.params:
            print ("COULD NOT FIND KEY, CREATE NEW KEY")
            page_store = []
            url = self._url + self._ext['group_picker']
            query_params = {
                'query': query,
                'exclude': exclude,
                'maxResults': self._searchrange
            }
            response = self._session.get(url,params=query_params)
            if response.status_code != 200:
                return None
            response = json.loads(response.text)
            for group in response['groups']:
                page_store.append((group['name'],group['html']))
            self._session.params[key] = page_store

        start = (page - 1) * limit
        end = (page * limit) - 1
        print ("LOAD KEY")
        return self._session.params[key][start:end]






# THIS BELOW PORTION IS FOR TESTING PURPOSES ONLY

jira = JiraConnector()

while 1:
    print "\n1 - login\n2 - logout\n3 - create user\n4 - get user\n5 - update user\n6 - delete user"
    print "7 - create group\n8 - get group\n9 - add user to group\n10 - delete user from group"
    print "11 - delete group\n12 - search user\n13 - all users\n14 - search group"

    sel = int(input('\nselection: '))
    if sel == 1:
        usr = str(input("username "))
        pwd = str(getpass.getpass('password '))
        print jira.login(usr, pwd)
    elif sel == 2:
        print jira.logout() # what parameters will I have to pass in later?
    elif sel == 3:
        name,email,disp,pwd = str(input("username email displayname password ")).split()
        print jira.create_user(name, email, disp, pwd)
    elif sel == 4:
        username = str(input("username"))
        print jira.get_user(username)
    elif sel == 5:
        name,email,disp,pwd = str(input("username email displayname password ")).split()
        print jira.update_user(name, email, disp, username)
    elif sel == 6:
        username = str(input("username "))
        print jira.delete_user(username)
    elif sel == 7:
        grpname = str(input("groupname "))
        print jira.create_group(grpname)
    elif sel == 8:
        grpname = str(input("groupname "))
        print jira.get_group(grpname)
    elif sel == 9:
        username,grpname = str(input("username groupname ")).split()
        print jira.add_user_group(username,grpname)
    elif sel == 10:
        username,grpname = str(input("username groupname ")).split()
        print jira.delete_user_group(username,grpname)
    elif sel == 11:
        grpname = str(input("groupname "))
        print jira.delete_group(grpname)
    elif sel == 12:
        query = str(input("what to search for: "))
        exclude = str(input("What to exclude: "))
        page = int(input('what page: '))
        limit = int(input('what limit: '))
        print jira.search_user(query, exclude, page, limit)
    elif sel == 13:
        print jira.all_users(1,50)
    elif sel == 14:
        query = str(input("what to search for: "))
        exclude = str(input("What to exclude: "))
        page = int(input('what page: '))
        limit = int(input('what limit: '))
        print jira.search_group(query, exclude, page, limit)
    else:
        print "NO BAD STOP! >:("