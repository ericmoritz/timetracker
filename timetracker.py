import dbm
import json
import os
from wsgiref import util, headers
from contextlib import closing
from StringIO import StringIO
import mimetypes
import re
from pprint import pprint

HERE = os.path.dirname(__file__)


def make_app(db, root):
    def application(environ, start_response):
        routes = (
            (r"^/projects$", collection_res),
            (r"^/projects/[^/]+/tasks$", collection_res),
            (r"^/projects/[^/]+/tasks/[^/]+$", member_res),
            (r"^/projects/[^/]+$", member_res),
            (r"^.+", static_res(root)),
        )
        environ['db'] = db

        return route_application(routes, environ)(environ, start_response)
    return application


def route_application(routes, environ):
    path_info = environ.get("PATH_INFO", "/")

    for route_pat, app in routes:
        match = re.match(route_pat, path_info)
        if match:
            return view_res(app, match.groups())

    return error_res("404 Not Found", [])

def body(environ):
    buffer = StringIO()
    fh = environ['wsgi.input']
    length = int(environ['CONTENT_LENGTH'])

    data = fh.read(length)
    buffer.write(data)
    buffer.seek(0)
    return buffer
    

def view_res(view, args):
    def inner(environ, start_response):
        return view(environ, start_response, *args)
    return inner


def error_res(status, headers, body=""):
    def inner(environ, start_response):
        start_response(status, headers)
        return body
    return inner


def static_res(root):
    def inner(environ, start_response):
        path_info = environ.get("PATH_INFO", "")
        local_path = os.path.join(root,
                                  "webroot",
                                  path_info.lstrip("/"))
        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, "index.html")

        if not os.path.exists(local_path):
            start_response("404 Not Found", [])
            return []
        elif not os.path.isfile(local_path):
            start_response("403 Forbidden", [])
            return []
        else:
            with closing(open(local_path, "r")) as fh:
                data = fh.read()

            mimetype, encoding = mimetypes.guess_type(local_path)
            if mimetype:
                headers = [("Content-Type", mimetype)]
            else:
                headers = []

            start_response("200 OK", headers)
            return data
    return inner


def json_res(sr, status, header_list, data):
    heads = headers.Headers(header_list)
    heads['Content-Type'] = "application/json"

    sr(status, heads.items())
    return json.dumps(data)

## Models
def path2member_key(path):
    bits = path.split("/")
    collection = "/".join(bits[:-1])
    member_key = bits[-1]
    
    return (collection, member_key)


def collection(db, path):
    index = json.loads(db.get(path, "[]"))
    return [json.loads(db[key]) for key in index]


def member(db, path):
    json_packet = db.get(path)
    if json_packet is not None:
        return json.loads(json_packet)


def store_member(db, path, data):
    collection, member_key = path2member_key(path)

    # update the member data
    data['id'] = path
    db[path] = json.dumps(data)

    # update the index
    index = set(json.loads(db.get(collection, "[]")))
    index.add(path)
    db[collection] = json.dumps(sorted(index))
    
def delete_member(db, path):
    collection, member_key = path2member_key(path)

    try:
        del db[path]
    except KeyError:
        return False

    # update the index
    index = set(json.loads(db.get(collection, "[]")))
    index.remove(path)
    db[collection] = json.dumps(sorted(index))

    return True
    
## HTTP Resources
def collection_res(environ, start_response):
    db = environ['db']
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']

    if method == "GET":
        data = collection(db, path)
        return json_res(start_response, "200 OK", [], data)
    else:
        return error_res("405 Not Allowed", [("Allow", "GET")])(environ, start_response)


def member_res(environ, start_response):
    db = environ['db']
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']

    if method == "GET":
        data = member(db, path)

        if data is None:
            return error_res("404 Not Found", [])(environ, start_response)
        else:
            return json_res(start_response, "200 OK", [], data)
    elif method == "PUT":
        data = json.load(body(environ))
        store_member(db, path, data)
        return json_res(start_response, "200 OK", [], data)
    elif method == "DELETE":
        if delete_member(db, path):
            return json_res(start_response, "200 OK", [], True)
        else:
            return error_res("404 Not Found", [])(environ, start_response)
    else:
        return error_res("405 Not Allowed", [("Allow", "GET")])(environ, start_response)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    HERE = os.path.dirname(__name__)
    db = dbm.open(os.path.join(HERE, "projects"), "c")


    httpd = make_server("", 8000, make_app(db, HERE))
    print "Listening on 0.0.0.0:8000"
    httpd.serve_forever()

