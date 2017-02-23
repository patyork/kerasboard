import requests
import sys, getopt
import numpy as np

import time
def usage():
    print('''-h --help : This screen\n-p --port = Port to listen on''')

if __name__ == '__main__':
    port = 8888
    delay = 1.0

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
            delay = arg

    id = 50
    while True:
        r = requests.get('http://localhost:%i/api' % port, params={'id': id, 'value': np.random.random() * 1000})
        time.sleep(delay)
        id += 1

