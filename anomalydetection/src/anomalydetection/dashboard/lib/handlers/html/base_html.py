# -*- coding: utf-8 -*-

import traceback

from anomalydetection.dashboard.lib.handlers.BaseHandler import BaseHandler
from anomalydetection.dashboard.lib.helpers.error import Error


class BaseHTMLHandler(BaseHandler):
    """
    Abstract Handler for HTML responses, this will render a template with some data, this
    class should be extended defining template, title, get, post, push, etc... methods
    """

    db = None
    template = None
    error_template = "500.html"
    maintenance = False

    def data_received(self, chunk):
        pass

    def write_error(self, status_code, **kwargs):
        """
        Write an error in HTML format.
        :param status_code:  The status code, 4xx or 5xx.
        :param kwargs:       A Keyword argument list.
        :return:             Prints an error.
        """
        self.set_header('Content-Type', 'text/html')

        # in debug mode, add traceback
        trace = []
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            for line in traceback.format_exception(*kwargs["exc_info"]):
                trace.append(line.strip())

        # Error object
        error = Error(status_code, self._reason, trace)

        # Print it
        self.print_error(error)

    def response(self, **kwargs):
        self.set_status(self.default_response_code)
        self.render(self.template, **kwargs)

    def print_error(self, error):
        self.set_status(error.code, error.message)
        self.render(self.error_template, error=error)
