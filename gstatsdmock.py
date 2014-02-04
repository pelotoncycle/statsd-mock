#!/usr/bin/python
# -*- coding: utf-8 -*-
import gevent
# import time
import pprint
import socket
from collections import deque

import gevent.socket as gsocket

STATSD_DEFAULT_PORT = 8125

class StatsdMockServer(object):

    _metric_types = {
        'c': 'counter',
        'g': 'gauge',
        't': 'timer',
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
                # print 'waiting for packet'
                msg, address = self.sock.recvfrom(self.recv_packet_size)
            except socket.error:
                # print 'not received yet, sleeping...'
                gevent.sleep(0.01)
            else:
                # print 'received!'
                # data = simplejson.loads(msg)
                # self._emit(data['type'], data['time'], data['data'])

                # TODO
                # self.messages.append(msg)
                print 'received: %s' % msg
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

        # value = chunks.popleft()
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
        print 'saved: %s => %s' % (metric_name, pprint.pformat(metric_data))

    # def _emit(self, event_type, time, data):
    #     if event_type not in self.events:
    #         self.events[event_type] = deque([])
    #     emit_data = dict(event_type=event_type, time=time, data=data)
    #     self.events[event_type].append(emit_data)
    #     # print 'put: %s' % pprint.pformat(emit_data)

    def stop(self):
        assert self.running is True
        self.running = False
        self.thread.join()
        self.sock.close()
        self.sock = None
        self.port = None
        self.bind_address = None

    def wait(self, metric_name, n):
        assert self.sock is not None
        if metric_name not in self.metrics:
            self.metrics[metric_name] = deque([])

        while len(self.metrics[metric_name]) < n:
            # print 'current: %d' % len(self.metrics[metric_name])
            # gevent.sleep(1.0)
            gevent.sleep()

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
    # emitter = UDPCubeEmitter('127.0.0.1')
    for i in range(n):
        # data = {'n': i, 'name': 'tomotaka'}
        # print 'sent! data=%s' % pprint.pformat(data)
        gauge.send('subtag', i*10)

    mock_server.wait('bigtag.subtag', n)
    mock_server.stop()
    mock_server.dump_events()


if __name__ == '__main__':
    gth = gevent.spawn(main)
    gth.join()
    print 'END'

