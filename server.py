from tornado import websocket, web, ioloop
import json
import numpy as np
import sys
import getopt
import socket

import sqlite3
conn = sqlite3.connect(':memory:')

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

cl = []

tmp_index = 0


def initialize_db(tmp_index):
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE stocks
                 (batch_id integer, random real)''')

    for i in range(20):
        c.execute('INSERT INTO stocks VALUES (?,?)', (tmp_index, np.random.random()*1000))

        # Save (commit) the changes
        conn.commit()
        tmp_index += 1

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    #conn.close()
    return tmp_index


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("static/index.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):
        get_params = None       # {'model': 7, etc...}
        if len(args) == 1 and len(args[0]) > 0:
            params = args[0].replace('/', '').strip()
            get_params = dict((k.strip(), v.strip()) for k,v in (item.split('=') for item in params.split('&')))

        if self not in cl:
            cl.append(self)

            c = conn.cursor()
            #datas = []
            #for row in c.execute('SELECT * FROM stocks order by 1'):
            #    data = json.dumps({"id": row[0], "value": row[1]})
            #    datas.append(data)

            #self.write_message(json.dumps(datas))


    def on_close(self):
        if self in cl:
            cl.remove(self)

class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        id = self.get_argument("id")
        value = self.get_argument("value")
        data = {"id": id, "value": value}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    @web.asynchronous
    def post(self):
        self.finish()

        values = json.loads(self.request.body)
        values = values['values']
        print values

        datas = []
        for value in values:
            data = json.dumps({"id": 0, "value": value})
            datas.append(data)

        for c in cl:
            c.write_message(json.dumps(datas))


class ApiHandler2(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        values = self.get_argument("values")

        datas = []
        for value in values:
            datas.append(json.dumps({"id": 0, "value": value}))
        for c in cl:
            c.write_message(json.dumps(datas))

    @web.asynchronous
    def post(self):
        self.finish()

        values = json.loads(self.request.body)

        datas = []
        for value in values['values']:
            data = json.dumps({"id": 0, "value": value})
            datas.append(data)

        for c in cl:
            c.write_message(json.dumps(datas))

app = web.Application([
    (r'/', IndexHandler),
    (r"/(.*\.html)", web.StaticFileHandler, dict(path='./static/')),
    (r"/lib/(.*\.(js|map|css))", web.StaticFileHandler, dict(path='./static/lib/')),
    (r'/ws(.*)', SocketHandler),
    (r'/api', ApiHandler),
    (r'/api2', ApiHandler2),
])


def usage():
    print(
        '-h --help\tThis screen\n'
        '--port=\tPort to listen on')

if __name__ == '__main__':
    port = 8888

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "h", ["help", "port="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("--port"):
            port = int(arg)
    try:
        app.listen(port)
        print('Listening on:\n\thttp://localhost:{0}/\n\tws://localhost:{1}/ws'.format(port, port))
    except socket.error as e:
        print('Port {0} is already in use. Please select a different port via the `--port=` flag.'.format(port))
        sys.exit(-1)
    tmp_index = initialize_db(tmp_index)
    ioloop.IOLoop.instance().start()
