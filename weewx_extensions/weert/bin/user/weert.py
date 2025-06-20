#
#  Copyright (c) 2017-2022 Tom Keffer <tkeffer@gmail.com>
#
#     See the file LICENSE for your full rights.
#

#
# See the WeeRT README file (https://github.com/MaffooClock/weewx-weert)
# for instructions on how to install this uploader in weewx.
#

import base64
import json
import math
import threading
import sys

import configobj
import weewx.restx
from queue import Queue
from weeutil.weeutil import to_int

from .config import config_defaults

try:
    # Test for new-style weewx logging by trying to import weeutil.logger
    import weeutil.logger
    import logging
    log = logging.getLogger(__name__)

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

except ImportError:
    # Old-style weewx logging
    import syslog

    def logmsg(level, msg):
        syslog.syslog(level, 'weert: %s:' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)


class WeeRT(weewx.restx.StdRESTful):
    """WeeWX service for uploading to the WeeRT server."""

    def __init__(self, engine, config_dict):
        super(WeeRT, self).__init__(engine, config_dict)

        # This utility will check the config_dict for any missing options. It returns None if
        # something is missing.
        weert_dict = weewx.restx.get_site_dict(config_dict, 'WeeRT', 'host', 'port', 'user', 'password')
        if weert_dict is None:
            return

        # Check to make sure this version of weewx supports JSON posts.
        # To do this, look for function weewx.restx.RESTThread.get_post_body
        try:
            getattr(weewx.restx.RESTThread, 'get_post_body')
        except AttributeError:
            loginf('WeeWX needs to be upgraded to V3.8 in order to run WeeRT')
            loginf('****   WeeRT upload skipped')
            return

        # Start with the defaults. Make a copy --- we will be modifying it
        weert_config = configobj.ConfigObj(config_defaults)['WeeRT']
        # Now merge in the overrides from the config file
        weert_config.merge(weert_dict)

        # Create and start a separate thread to do the actual posting.
        self.loop_queue = Queue()
        self.archive_thread = WeeRTThread(self.loop_queue, **weert_config)
        self.archive_thread.start()

        # Bind to the NEW_LOOP_PACKET event.
        self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
        loginf("LOOP packets will be posted to %s:%s"
               % (weert_config['host'], weert_config['port']))

    def new_loop_packet(self, event):
        "Called when a new loop packet arrives"
        # Stuff the packet into the queue
        self.loop_queue.put(event.packet)


class WeeRTThread(weewx.restx.RESTThread):
    """Thread that posts to a WeeRT server"""

    def __init__(self, queue,
                 host, port,
                 user, password,
                 measurement,
                 platform, stream,
                 loop_filters,
                 protocol_name="WeeRT",
                 post_interval=None, max_backlog=sys.maxsize, stale=None,
                 log_success=True, log_failure=True,
                 timeout=2, max_tries=1, retry_wait=5, retry_login=3600,
                 softwaretype="weewx-%s" % weewx.__version__,
                 skip_upload=False):

        """
        Initializer for the WeeRThread class.

        Parameters specific to this class:

          host:
          port: The host and port of the WeeRT server
          
          user:
          password: The username and password to be send

          measurement: The InfluxDB measurement name to use.

          platform: The platform name

          stream: The stream name

          loop_filters: A data structure holding what values are to be emitted.
        """
        super(WeeRTThread, self).__init__(queue,
                                          protocol_name=protocol_name,
                                          post_interval=post_interval,
                                          max_backlog=max_backlog,
                                          stale=stale,
                                          log_success=log_success,
                                          log_failure=log_failure,
                                          timeout=timeout,
                                          max_tries=max_tries,
                                          retry_wait=retry_wait,
                                          retry_login=retry_login,
                                          softwaretype=softwaretype,
                                          skip_upload=skip_upload)

        self.host = host
        self.port = to_int(port)
        self.user = user
        self.password = password
        self.measurement = measurement
        self.platform = platform
        self.stream = stream

        # Compile the filter functions for the loop packets:
        self.filter_funcs = _compile_filters(loop_filters)

    def format_url(self, _):
        """Override and return the URL used to post to the WeeRT server"""

        url = "http://%s:%s/api/v1/measurements/%s/packets" % (self.host, self.port, self.measurement)
        return url

    def get_request(self, url):
        """Override and add user and password"""

        # Get the basic Request from my superclass
        request = super(WeeRTThread, self).get_request(url)

        # Create a base64 byte string with the authorization info
        base64string = base64.b64encode(('%s:%s' % (self.user, self.password)).encode())
        # Add the authentication header to the request:
        request.add_header("Authorization", b"Basic %s" % base64string)
        return request

    def get_post_body(self, packet):
        """Override, then supply the body and MIME type of the POST"""

        out_packet = {}
        # Subject all the types to be sent to a filter function.
        for k in self.filter_funcs:
            # This will include only types included in the filter functions.
            # If there is not enough information in the packet to support the filter
            # function, then an exception of type NameError will be raised, 
            # and the type will be skipped.
            try:
                out_packet[k] = eval(self.filter_funcs[k], {"math": math}, packet)
            except NameError:
                pass

        body = {
            "measurement": self.measurement,
            "tags": {"platform": self.platform, "stream": self.stream},
            "timestamp": int(packet["dateTime"] * 1000),  # Convert to milliseconds
            "fields": out_packet
        }
        json_body = json.dumps(body)
        return json_body, 'application/json'


def _compile_filters(loop_filters):
    """Compile the filter statements"""
    filter_funcs = {}
    for obs_type in loop_filters:
        filter_funcs[obs_type] = compile(loop_filters[obs_type], "WeeRT", 'eval')
    return filter_funcs
