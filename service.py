"""
Tutorial - Multiple objects

This tutorial shows you how to create a site structure through multiple
possibly nested request handler objects.
"""

import cherrypy
import mysql.connector
import datetime

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
root = HomePage()
root.joke = JokePage()
root.links = LinksPage()
root.pets = PetInfoPage()

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
    cherrypy.quickstart(root, config=serviceconf)
else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.tree.mount(root, config=serviceconf)

