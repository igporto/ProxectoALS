#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import time
from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import images
import datetime
import jinja2

#Definicion del Enviroment
JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+"/templates"),
                                      extensions=["jinja2.ext.autoescape"],
                                      autoescape=True)

class User(ndb.Model):
    id_user = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)

class Escritor(ndb.Model):
    nome = ndb.StringProperty(required=True)
    apelidos = ndb.StringProperty(required=True)
    webPersoal = ndb.StringProperty(required=True)
    wiki = ndb.StringProperty(required=True)
    usuario = ndb.KeyProperty(kind=User)

class Libro(ndb.Model):
    titulo = ndb.StringProperty(required=True)
    xenero = ndb.StringProperty(required=True)
    sinopse = ndb.StringProperty(default="")
    autor = ndb.KeyProperty(kind=Escritor)
    portada = ndb.BlobProperty(required=True)
    valoracion = ndb.FloatProperty(default=0)
    usuario = ndb.KeyProperty(kind=User)


class Comentario(ndb.Model):
    libro = ndb.KeyProperty(kind=Libro)
    usuario = ndb.KeyProperty(kind=User)
    texto = ndb.StringProperty(required=True)
    valoracion = ndb.IntegerProperty(required=True)
    data = ndb.DateTimeProperty(required=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            people = User.query().order(User.name)
            # Look for the user's information
            user_id = user.user_id()
            name_info = user.nickname()
            stored_user = User.query(User.id_user == user_id)

            if stored_user.count() == 0:
                # Store the information
                img = User(id_user=user_id, name=name_info)
                img.put()
                time.sleep(1)

            labels = {
                "username": user.nickname().partition("@")[0],
                "usuario": user.nickname(),
                "user_logout": users.create_logout_url("/")
            }
            template = JINJA_ENVIRONMENT.get_template("inicio.html")
            self.response.write(template.render(labels))
        else:
            labels = {
                "user_login": users.create_login_url("/")
            }
            template = JINJA_ENVIRONMENT.get_template("login.html")
            self.response.write(template.render(labels))

class LibrosHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            libros = Libro.query()

            add = self.request.get("add")
            delete = self.request.get("delete")
            erro = self.request.get("erro")
            ok = self.request.get("ok")
            escritores = Escritor.query()

            values = {'libros': libros,
                      "escritores": escritores,
                      "add": add,
                      "delete": delete,
                      "erro": erro,
                      "ok": ok,
                      "usuario": user.nickname(),
                      "user": user,
                      "user_logout": users.create_logout_url("/")
                      }

            template = JINJA_ENVIRONMENT.get_template("libros.html")
            self.response.write(template.render(values))
        else:
            self.redirect("/")

class AddLibroHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            escritores = Escritor.query().order(Escritor.apelidos)
            user = users.get_current_user()
            values = {'escritores': escritores,
                      "usuario": user.nickname(),
                      "user_logout": users.create_logout_url("/")
                      }

            template = JINJA_ENVIRONMENT.get_template("Libro_ADD.html")
            self.response.write(template.render(values))
        else:
            labels = {
                "user_login": users.create_login_url("/")
            }
            template = JINJA_ENVIRONMENT.get_template("login.html")
            self.response.write(template.render(labels))


    def post(self):
        titulo = self.request.get("titulo").capitalize()
        if titulo:
            id_autor = self.request.get("autor")
            id_autor = int(id_autor)
            # Store the added image
            image_file = self.request.get("portada", None)
            autor_key = ndb.Key(Escritor, id_autor)
            libros = Libro.query(Libro.titulo == titulo, Libro.autor == autor_key)
            if libros.count() == 0:
                xenero = self.request.get("xenero")
                sinopse = self.request.get("sinopse")
                usuario = users.get_current_user().user_id()
                print("USER"+str(usuario))

                libro = Libro(titulo=titulo, xenero=xenero, sinopse=sinopse, autor=autor_key, portada=image_file, usuario = ndb.Key(User,usuario))
                libro.put()
                time.sleep(1)

                self.redirect("/libros?add=True")
            else:
                self.redirect("/libros?erro=True")

class EditLibroHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            id_Libro = self.request.get("id")
            if id_Libro:
                id_Libro = int(id_Libro)
                libro_key = ndb.Key(Libro, id_Libro)
                libro = Libro.query(Libro.key == libro_key).get()
                escritores = Escritor.query()


                if libro:
                    values = {"libro": libro,
                              "usuario": users.get_current_user().nickname(),
                              "escritores": escritores,
                              "user_logout": users.create_logout_url("/")
                              }
                    template = JINJA_ENVIRONMENT.get_template("Libro_EDIT.html")
                    self.response.write(template.render(values))
                else:
                    self.redirect("/libros")

        else:
            labels = {
                "user_login": users.create_login_url("/")
            }
            template = JINJA_ENVIRONMENT.get_template("login.html")
            self.response.write(template.render(labels))

    def post(self):
        id_autor = int(self.request.get("autor"))
        titulo = self.request.get("titulo")
        autor_key = ndb.Key(Escritor, id_autor)

        libros = Libro.query(Libro.titulo == titulo, Libro.autor == autor_key)
        if libros.count() == 0:
            id_Libro = self.request.get("id")
            libro_key = ndb.Key(Libro, int(id_Libro))
            libro = Libro.query(Libro.key == libro_key).get()

            libro.titulo = self.request.get("titulo").capitalize()
            libro.xenero = self.request.get("xenero")
            libro.sinopse = self.request.get("sinopse")
            libro.autor = ndb.Key(Escritor, int(self.request.get("autor")))

            if(self.request.get("portada")!=""):
                # Store the added image
                image_file = self.request.get("portada", None)
                libro.portada = image_file

            libro.put()
            time.sleep(1)

            self.redirect("/libros?ok=True")
        else:
            self.redirect("/libros?erro=True")

class DeleteLibroHandler(webapp2.RequestHandler):
    def get(self):
        id_Libro = self.request.get("id")
        libro = Libro.query(Libro.key == ndb.Key(Libro, int(id_Libro))).get()

        comentarios = Comentario.query(Comentario.libro == ndb.Key(Libro, int(id_Libro)))

        for comentario in comentarios:
            comentario.key.delete()
            time.sleep(1)

        libro.key.delete()
        time.sleep(1)

        self.redirect("/libros?delete=True")

class AddComentarioHandler(webapp2.RequestHandler):
    def post(self):

        id_Libro = self.request.get("id")
        print("ID:"+str(id_Libro))
        texto = self.request.get("comentario")
        valoracion = int(self.request.get("valoracion"))
        data = datetime.datetime.today()
        id_Usuario = users.get_current_user().user_id()
        libro_key = ndb.Key(Libro, int(id_Libro))
        libro = Libro.query(Libro.key == libro_key).get()

        comentario = Comentario(texto=texto,
                                usuario=ndb.Key(User, id_Usuario),
                                libro=libro_key,
                                valoracion=valoracion,
                                data=data)

        numComentarios = Comentario.query(Comentario.libro == ndb.Key(Libro, int(id_Libro))).count()
        valoracionMedia = ((libro.valoracion * numComentarios) + comentario.valoracion)
        comentario.put()
        time.sleep(1)
        numComentarios = Comentario.query(Comentario.libro == ndb.Key(Libro, int(id_Libro))).count()
        libro.valoracion = round(valoracionMedia/numComentarios,2)
        libro.put()
        time.sleep(1)

        self.redirect("/rateLibro?id="+str(id_Libro))

    def get(self):
        user = users.get_current_user()
        if user:
            id_Libro = self.request.get("id")
            libro = Libro.query(Libro.key == ndb.Key(Libro, int(id_Libro))).get()
            comentarios = Comentario.query(Comentario.libro == ndb.Key(Libro, int(id_Libro)))
            escritor = Escritor.query(Escritor.key == libro.autor).get()

            print(comentarios.count())
            user = users.get_current_user()
            usuarios = User.query()
            values = {"libro": libro,
                      "escritor": escritor,
                      "comentarios": comentarios,
                      "usuario": user.nickname(),
                      "usuarioActual": user.user_id(),
                      "usuarios":usuarios,
                      "user_logout": users.create_logout_url("/")
            }
            template = JINJA_ENVIRONMENT.get_template("rateLibro.html")
            self.response.write(template.render(values))

        else:
            labels = {
                "user_login": users.create_login_url("/")
            }
            template = JINJA_ENVIRONMENT.get_template("login.html")
            self.response.write(template.render(labels))

class deleteComentarioHandler(webapp2.RequestHandler):
    def post(self):
        id_Comentario = self.request.get("id")
        comentario = Comentario.query(Comentario.key == ndb.Key(Comentario, int(id_Comentario))).get()
        id_Libro = comentario.libro.id()
        libro_key = ndb.Key(Libro, int(id_Libro))

        libro = Libro.query(Libro.key == libro_key).get()

        numComentarios = Comentario.query(Comentario.libro == ndb.Key(Libro, int(id_Libro))).count()
        if(numComentarios>1):
            valoracionMedia = ((libro.valoracion*numComentarios)-comentario.valoracion)/(numComentarios-1)
        else:
            valoracionMedia=0
        libro.valoracion = round(valoracionMedia, 2)
        libro.put()
        time.sleep(1)

        print(id_Libro)
        comentario.key.delete()
        time.sleep(1)



        self.redirect("/rateLibro?id="+str(id_Libro))

class editComentarioHandler(webapp2.RequestHandler):
    def post(self):
        id_Comentario = self.request.get("id")
        comentario = Comentario.query(Comentario.key == ndb.Key(Comentario, int(id_Comentario))).get()
        id_Libro = comentario.libro.id()
        libro = Libro.query(Libro.key == ndb.Key(Libro, id_Libro)).get()

        numComentarios = Comentario.query(Comentario.libro == ndb.Key(Libro, int(id_Libro))).count()
        valoracionMedia = ((libro.valoracion * numComentarios) - comentario.valoracion)

        print("SACANDOO"+str(valoracionMedia)+" NV: "+self.request.get("valoracion"))

        texto = self.request.get("comentario")
        comentario.texto = texto
        comentario.valoracion = int(self.request.get("valoracion"))
        if(numComentarios>1):
            valoracionMedia = ((valoracionMedia * (numComentarios-1)) + int(self.request.get("valoracion")))
        else:
            valoracionMedia = self.request.get("valoracion")

        print("METENDOO" + str(valoracionMedia / numComentarios))
        comentario.put()
        time.sleep(1)

        libro.valoracion = round(valoracionMedia / numComentarios, 2)


        libro.put()
        time.sleep(1)

        self.redirect("/rateLibro?id="+str(id_Libro))

class escritoresHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            escritores = Escritor.query()

            add = self.request.get("add")
            delete = self.request.get("delete")
            erro = self.request.get("erro")
            ok = self.request.get("ok")
            values = {
                "usuario": user.nickname(),
                'escritores': escritores,
                "user":user,
                "add":add,
                "erro": erro,
                "ok": ok,
                "delete":delete,
                "user_logout": users.create_logout_url("/")
            }

            template = JINJA_ENVIRONMENT.get_template("escritores.html")
            self.response.write(template.render(values))
        else:
            labels = {
                "user_login": users.create_login_url("/")
            }
            template = JINJA_ENVIRONMENT.get_template("login.html")
            self.response.write(template.render(labels))

class AddEscritorHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            user = users.get_current_user()
            values = {
                    "usuario": user.nickname(),
                    "user_logout": users.create_logout_url("/")
            }

            template = JINJA_ENVIRONMENT.get_template("Escritor_ADD.html")
            self.response.write(template.render(values))
        else:
            labels = {
                "user_login": users.create_login_url("/")
            }
            template = JINJA_ENVIRONMENT.get_template("login.html")
            self.response.write(template.render(labels))


    def post(self):
        nome = self.request.get("nome")
        apelidos = self.request.get("apelidos")
        escritores = Escritor.query(Escritor.nome == nome, Escritor.apelidos == apelidos)

        if escritores.count() == 0:
            webPersoal = self.request.get("web")
            wiki = self.request.get("wiki")
            usuario = users.get_current_user().user_id()

            escritor = Escritor(nome=nome, apelidos=apelidos, webPersoal=webPersoal, wiki=wiki, usuario= ndb.Key(User,usuario))
            escritor.put()
            time.sleep(1)

            self.redirect("/escritores?add=True")
        else:
            self.redirect("/escritores?erro=True")

class DeleteEscritorHandler(webapp2.RequestHandler):
    def get(self):
        id_Escritor = self.request.get("id")
        escritor = Escritor.query(Escritor.key == ndb.Key(Escritor, int(id_Escritor))).get()

        libros = Libro.query(Libro.autor == ndb.Key(Escritor, int(id_Escritor)))

        for libro in libros:
            libro.key.delete()
            time.sleep(1)

        escritor.key.delete()
        time.sleep(1)

        self.redirect("/escritores?delete=True")

class EditEscritorHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            id_Escritor = self.request.get("id")
            if id_Escritor:
                id_Escritor = int(id_Escritor)
                escritor_key = ndb.Key(Escritor, id_Escritor)
                escritor = Escritor.query(Escritor.key == escritor_key).get()

                if escritor:
                    values = {"escritor": escritor,
                              "usuario": users.get_current_user().nickname(),
                              "user_login": users.create_login_url("/"),
                              "user_logout": users.create_logout_url("/")
                              }

                    template = JINJA_ENVIRONMENT.get_template("Escritor_EDIT.html")
                    self.response.write(template.render(values))
                else:
                    self.redirect("/libros")

        else:
            labels = {
                "user_login": users.create_login_url("/")
            }
            template = JINJA_ENVIRONMENT.get_template("login.html")
            self.response.write(template.render(labels))

    def post(self):
        nome = self.request.get("nome")
        apelidos = self.request.get("apelidos")

        escritores = Escritor.query(Escritor.nome == nome and Escritor.apelidos == apelidos)

        if escritores.count() == 0:
            escritor_key = ndb.Key(Escritor, int(self.request.get("id")))
            escritor = Escritor.query(Escritor.key == escritor_key).get()

            escritor.nome = self.request.get("nome")
            escritor.apelidos = self.request.get("apelidos")

            escritor.webPersoal = self.request.get("web")
            escritor.wiki = self.request.get("wiki")

            escritor.put()
            time.sleep(1)

            self.redirect("/escritores?ok=True")
        else:
            self.redirect("/escritores?erro=True")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/libros', LibrosHandler),
    ('/addLibro', AddLibroHandler),
    ('/editLibro', EditLibroHandler),
    ('/deleteLibro', DeleteLibroHandler),
    ('/rateLibro', AddComentarioHandler),
    ('/deleteComentario', deleteComentarioHandler),
    ('/editComentario', editComentarioHandler),
    ('/escritores', escritoresHandler),
    ('/addEscritor', AddEscritorHandler),
    ('/editEscritor', EditEscritorHandler),
    ('/deleteEscritor', DeleteEscritorHandler),


], debug=True)
