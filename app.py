from tornado import websocket, web, ioloop
import json
import numpy as np
import sys, getopt

import sqlite3
conn = sqlite3.connect(':memory:')

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

    def open(self):
        if self not in cl:
            cl.append(self)

            c = conn.cursor()
            datas = []
            for row in c.execute('SELECT * FROM stocks order by 1'):
                data = json.dumps({"id": row[0], "value": row[1]})
                datas.append(data)

            self.write_message(json.dumps(datas))




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
        pass

class ApiHandler2(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        values = self.get_argument("values")

        datas = []
        for value in values:
            datas.append(json.dumps({"id": 0, "value": value}))
        data = json.dumps(datas)
        for c in cl:
            c.write_message(data)

    @web.asynchronous
    def post(self):
        pass

app = web.Application([
    (r'/', IndexHandler),
    (r"/(.*\.html)", web.StaticFileHandler, dict(path='./static/')),
    (r"/lib/(.*\.(js|map|css))", web.StaticFileHandler, dict(path='./static/lib/')),
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
    (r'/api2', ApiHandler2),
])

def usage():
    print('''-h --help : This screen\n-p --port = Port to listen on''')

if __name__ == '__main__':
    port = 8888

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hp", ["help", "port="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-p", "--port"):
            port = arg

    app.listen(port)
    tmp_index = initialize_db(tmp_index)
    ioloop.IOLoop.instance().start()
