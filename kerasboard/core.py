from keras import callbacks
import time
import requests
import numpy as np


class KerasBoardClient(callbacks.Callback):
    def __init__(self, timing_duration=2.0, updates_per_second=5, url='http://localhost:8889/api2'):
        super(KerasBoardClient, self).__init__()

        self.timing_duration = timing_duration
        self.target_updates_per_second = updates_per_second
        self.url = url

        # Internal statistics to send more data in each write/POST
        self.in_fit_mode = True
        self.batches_per_second = 0.0
        self.in_fit_mode_start = None
        self.batches_per_update = 1.0

        # Data Queue
        self.batches_in_queue = 0
        self.data_queue = []

    def _send_data(self):
        r = requests.post(self.url, json={'values': self.data_queue})
        return r.status_code == 200

    def on_train_begin(self, logs={}):
        self.in_fit_mode = True
        self.in_fit_mode_start = time.time()

    def on_batch_end(self, batch, logs={}):

        self.batches_in_queue += 1
        self.data_queue.append(logs.get('loss').tolist())

        if self.in_fit_mode:
            self.batches_per_second += 1

            if self.timing_duration <= (time.time() - self.in_fit_mode_start):
                self.in_fit_mode = False
                dur = time.time() - self.in_fit_mode_start

                self.batches_per_update = int(np.ceil(self.batches_per_second / dur / self.target_updates_per_second))

                if self._send_data():
                    self.batches_in_queue = 0
                    self.data_queue = []

        elif self.batches_in_queue >= self.batches_per_update:
            if self._send_data():
                self.batches_in_queue = 0
                self.data_queue = []

    def on_epoch_end(self, epoch, logs={}):
        if len(self.data_queue) > 0:
            self._send_data()
