# -*- coding: utf-8 -*-

import webapp2
import jinja2
import os
from models import Sporocilo
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)

class BaseHandler(webapp2.RequestHandler):
    def render_template(self, filename, params_dict):
        template = jinja_env.get_template(filename)
        return self.response.write(template.render(params_dict))

class VnosHandler(BaseHandler):
    def get(self):

        params = {}

        user = users.get_current_user()
        if user:
            # Prijavljeni uporabnik
            params["prijavljen"] = True
            params["url"] = users.create_logout_url('/')
            params["user"] = user
        else:
            # Neprijavljeni uporabnik
            params["prijavljen"] = False
            params["url"] = users.create_login_url('/')

        return self.render_template("vnos.html", params)

class RezultatHandler(webapp2.RequestHandler):
    def post(self):
        sporocilo = self.request.get("sporocilo")

        user = users.get_current_user()
        sporocilo_db = Sporocilo(vnos=sporocilo, avtor=user.email())
        sporocilo_db.put()

        self.redirect("/seznam")

class SeznamHandler(webapp2.RequestHandler):
    def get(self):

        params = {}
        params["sporocila"] = Sporocilo.query(Sporocilo.izbrisano == False).fetch()
        params["uporabnik"] = users.get_current_user()
        template = jinja_env.get_template("seznam.html")
        return self.response.write(template.render(params))

class PosameznoSporociloHandler(webapp2.RequestHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        template = jinja_env.get_template("sporocilo.html")
        return self.response.write(template.render({"sporocilo": sporocilo}))

class BrisiHandler(webapp2.RequestHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.izbrisano = True
        sporocilo.put()

        # Ce zelim dejanski izbris!
        # sporocilo.key.delete()

        return self.redirect("/seznam")

class UrediHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        return self.render_template("uredi.html", {"s": sporocilo})

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        nova_vsebina = self.request.get("sporocilo")

        sporocilo.vnos = nova_vsebina
        sporocilo.put()
        return self.redirect("/seznam")

# URLs
app = webapp2.WSGIApplication([
    webapp2.Route('/', VnosHandler),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam', SeznamHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/brisi', BrisiHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/uredi', UrediHandler)
], debug=True)
