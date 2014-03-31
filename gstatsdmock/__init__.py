#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import gevent
import pprint
import socket
from collections import deque

import gevent.socket as gsocket

STATSD_DEFAULT_PORT = 8125


class StatsdTimeOutError(Exception):
    pass


class StatsdMockServer(object):

    _metric_types = {
        'c': 'counter',
        'g': 'gauge',
        'ms': 'timer',
        'r': 'raw'
    }

    def __init__(self, recv_packet_size=65535):
        self.sock = None
        self.port = None
        self.bind_address = None
        self.recv_packet_size = recv_packet_size
        self.metrics = {}

    def start(self, bind_address='127.0.0.1', port=STATSD_DEFAULT_PORT):
        if self.sock is not None:
            raise StandardError('UDPCubeMockServer has already started')
        self._prepare_socket(port, bind_address)
        self.thread = gevent.spawn(self._run)

    def _run(self):
        self.running = True
        while self.running:
            try:
                msg, address = self.sock.recvfrom(self.recv_packet_size)
            except socket.error:
                gevent.sleep(0.01)
            else:
                metric_name, value, metric_type, rate, timestamp = self._parse_packet(msg) 
                self._log(metric_name, value, metric_type, rate, timestamp)

    def _prepare_socket(self, port, bind_address):
        assert self.sock is None
        self.port = port
        self.bind_address = bind_address
        self.sock = gsocket.socket(gsocket.AF_INET, gsocket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.bind((self.bind_address, self.port))

    def _parse_packet(self, packet):
        chunks = deque(packet.split('|'))
        metric_name_and_value = chunks.popleft()

        metric_name, value = metric_name_and_value.split(':')

        metric_type = chunks.popleft()
        if metric_type == 'r':  # raw type will add timestamp
            timestamp = int(chunks.popleft())
        else:
            timestamp = None
        if 0 < len(chunks) and chunks[0][0] == '@':  # rate added?
            rate = float(chunks.popleft()[1:])
        else:
            rate = 1.0
        metric_type = self._metric_types[metric_type]  # 'c' => 'counter'
        return (metric_name, value, metric_type, rate, timestamp)

    def _log(self, metric_name, value, metric_type, rate, timestamp):
        if metric_name not in self.metrics:
            self.metrics[metric_name] = deque([])
        metric_data = dict(
            value=value,
            type=metric_type,
            rate=rate,
            timestamp=timestamp
        )
        self.metrics[metric_name].append(metric_data)

    def stop(self):
        assert self.running is True
        self.running = False
        self.thread.join()
        self.sock.close()
        self.sock = None
        self.port = None
        self.bind_address = None

    def wait(self, metric_name, n, timeout_msec=0):
        assert self.sock is not None
        time_msec_start = int(time.time() * 1000)
        if metric_name not in self.metrics:
            self.metrics[metric_name] = deque([])

        while len(self.metrics[metric_name]) < n:
            gevent.sleep()
            if 0 < timeout_msec and time_msec_start + timeout_msec < int(time.time() * 1000):
                raise StatsdTimeOutError('wait() for metric \'%s\' timed out' % metric_name)

    def dump_events(self):
        print '========StatsdMockServer'
        for metric_name in self.metrics:
            print '-----%s' % metric_name
            i = 1
            for metric_data in self.metrics[metric_name]:
                print '[%d] %s' % (i, pprint.pformat(metric_data))
                i += 1


def main():
    import statsd
    mock_server = StatsdMockServer()
    mock_server.start('127.0.0.1')
    print 'hello'

    statsd_connection = statsd.Connection(host='127.0.0.1', port=STATSD_DEFAULT_PORT)
    statsd_client = statsd.Client('bigtag', statsd_connection)
    gauge = statsd_client.get_client(class_=statsd.Gauge)

    n = 5
    for i in range(n):
        gauge.send('subtag', i*10)

    mock_server.wait('bigtag.subtag', n)
    mock_server.stop()
    mock_server.dump_events()


if __name__ == '__main__':
    gth = gevent.spawn(main)
    gth.join()
    print 'END'

