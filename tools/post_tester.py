import requests
import sys, getopt
import numpy as np
import json

import time
def usage():
    print('''-h --help : This screen\n-p --port = Port to listen on\n-d --delay = delay in milliseconds''')

if __name__ == '__main__':
    port = 8888
    delay = 1000
    type = 'POST'

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hpd", ["help", "port=", "delay="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-d", "--delay"):
            delay = float(arg)

    id = 50
    while True:
        try:
            if type == 'POST':
                r = requests.post('http://localhost:%s/api' % port, json={'values': [0.12, 0.23, np.random.random()]})
            else:
                r = requests.get('http://localhost:%s/api' % port, params={'id': id, 'value': np.random.random() * 1000})
            time.sleep(delay / 1000)
        except requests.ConnectionError:
            time.sleep(delay*5. / 1000.)

        id += 1

