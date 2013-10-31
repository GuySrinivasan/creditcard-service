"""
Pages and functionality:
1. landing page
2. choose your username from a dropdown or add a new username
3. page with credit card info and dropdown to switch between cards
4. allow entering comments on that page
Stretch. page with pending notifications or requests for info
"""

import cherrypy
import mysql.connector
import datetime

class CreditCardHome:
    def __init__(self, user):
        self.header = '''Our Credit Cards'''
        self.usernames = self.sqlGetUsernames()
        self.username = self.usernames[0]
        self.debug = []

    def index(self):
        self.usernames = self.sqlGetUsernames()
        self.changeUser(self.username)
            
        page = [self.header]
        page.append(self.createWelcome(self.username))
        page.append(self.createDropdown(self.usernames))
        page.append(self.createAddNew())
        page.append(self.createDebuggingInfo())
        return "".join(["<p>{}</p>".format(x) for x in page])
    index.exposed = True

    def switchUser(self, username=None):
        self.changeUser(username)
        return self.index()
    switchUser.exposed = True

    def addNewUser(self, username=None):
        self.sqlAddUsername(username)
        self.usernames = self.sqlGetUsernames()
        self.changeUser(username)
        return self.index()
    addNewUser.exposed = True

    def sqlAddUsername(self, username):
        cnx = mysql.connector.connect(
            user='creditcarduser',
            password='password',
            database='creditcard')
        cursor = cnx.cursor()
        checkQuery = ("SELECT COUNT(name) FROM users WHERE name='{}';".format(username))
        self.debug.append(checkQuery)
        cursor.execute(checkQuery)
        if int(cursor.fetchone()[0]) == 0:
            insertQuery = ("INSERT INTO users (name) VALUES ('{}');".format(username))
            self.debug.append(insertQuery)
            cursor.execute(insertQuery)
        cnx.commit()
        cursor.close()
        cnx.close()

    def sqlGetUsernames(self):
        cnx = mysql.connector.connect(
            user='creditcarduser',
            password='password',
            database='creditcard')
        cursor = cnx.cursor()
        query = ("SELECT name FROM users")
        cursor.execute(query)
        usernames = []
        for name in cursor:
            usernames.append(name[0])
        cursor.close()
        cnx.close()
        return usernames

    def changeUser(self, username):
        if (username in self.usernames):
            self.username = username
        else:
            self.username = self.usernames[0]

    def createWelcome(self, username):
        return '''Welcome, {}.'''.format(username)

    def createDropdown(self, usernames):
        dropdown = '''
<form action="switchUser" method="post">
    <p>Switch user</p>
    {}
    <p><input type="submit" value="Switch"/></p>
</form>
'''
        userOptionTemplate = '''
<input type="radio" name="username" value="{}">{}
'''
        userOptions = "<br>".join([userOptionTemplate.format(x,x) for x in usernames])
        return dropdown.format(userOptions)

    def createAddNew(self):
        form = '''
<form action="addNewUser" method="post">
    <p>Add new user</p>
    <input type="text" name="username" value="" size="15" maxlength="40"/>
    <p><input type="submit" value="Add"/></p>
</form>'''
        return form

    def createDebuggingInfo(self):
        return "<br>".join(self.debug)
    
class HomePage:
    def index(self):
        return '''
            <p>Hi, this is the home page! Check out the other
            fun stuff on this site:</p>
            
            <ul>
                <li><a href="/pets/">Pet info</a></li>
                <li><a href="/joke/">A silly joke</a></li>
                <li><a href="/links/">Useful links</a></li>
            </ul>'''
    index.exposed = True

class PetInfoPage:
    def index(self):
        intro = '''<p>These are the pets we know about:</p>'''

        listsetup = '''<ul>{}</ul>'''

        listelement = '''<li>{} has a {} named {} that was born on {:%d %b %Y}</li>'''
        petlist = self.retrieve_pets(listelement)

        ending = '''<p>[<a href="../">Return</a>]</p>'''

        page = intro + listsetup.format(petlist) + ending
        return page
    index.exposed = True

    def retrieve_pets(self, pattern):
        cnx = mysql.connector.connect(
            user='creditcarduser',
            password='password',
            database='menagerie')
        cursor = cnx.cursor()
        query = ("SELECT name, owner, species, birth FROM pet")
        cursor.execute(query)
        petlist = []
        for (name, owner, species, birth) in cursor:
            petlist.append(pattern.format(owner, species, name, birth))
        cursor.close()
        cnx.close()
        return "".join(petlist)

class JokePage:
    def index(self):
        return '''
            <p>"In Python, how do you create a string of random
            characters?" -- "Read a Perl file!"</p>
            <p>[<a href="../">Return</a>]</p>'''
    index.exposed = True


class LinksPage:
    def __init__(self):
        # Request handler objects can create their own nested request
        # handler objects. Simply create them inside their __init__
        # methods!
        self.extra = ExtraLinksPage()
    
    def index(self):
        # Note the way we link to the extra links page (and back).
        # As you can see, this object doesn't really care about its
        # absolute position in the site tree, since we use relative
        # links exclusively.
        return '''
            <p>Here are some useful links:</p>
            
            <ul>
                <li><a href="http://www.cherrypy.org">The CherryPy Homepage</a></li>
                <li><a href="http://www.python.org">The Python Homepage</a></li>
            </ul>
            
            <p>You can check out some extra useful
            links <a href="./extra/">here</a>.</p>
            
            <p>[<a href="../">Return</a>]</p>
        '''
    index.exposed = True


class ExtraLinksPage:
    def index(self):
        # Note the relative link back to the Links page!
        return '''
            <p>Here are some extra useful links:</p>
            
            <ul>
                <li><a href="http://del.icio.us">del.icio.us</a></li>
                <li><a href="http://www.mornography.de">Hendrik's weblog</a></li>
            </ul>
            
            <p>[<a href="../">Return to links page</a>]</p>'''
    index.exposed = True


# Of course we can also mount request handler objects right here!
#root = HomePage()
#root.joke = JokePage()
#root.links = LinksPage()
#root.pets = PetInfoPage()

# Remember, we don't need to mount ExtraLinksPage here, because
# LinksPage does that itself on initialization. In fact, there is
# no reason why you shouldn't let your root object take care of
# creating all contained request handler objects.


import os.path
serviceconf = os.path.join(os.path.dirname(__file__), 'service.conf')

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    cherrypy.quickstart(CreditCardHome("Guy"), config=serviceconf)
else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.tree.mount(root, config=serviceconf)

