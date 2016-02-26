# -*- coding: utf-8 -*-

import inspect
import logging
import os


class DebugLogger(logging.Logger):
    def debug(self, msg=None, *args, **kwargs):
        frm_info = inspect.stack()[1]
        method, frm = frm_info[3], frm_info[0]
        filename = os.path.split(frm_info[1])[-1]
        lineno = str(frm_info[2])
        if 'self' in frm.f_locals:
            method = frm.f_locals['self'].__class__.__name__ + '.' + method
        elif 'cls' in frm.f_locals:
            method = frm.f_locals['cls'].__name__ + '.' + method
        if not method.startswith('<'):
            method += '()'
        msg = ':'.join([filename, lineno, method] + [msg] * (msg is not None))
        logging.Logger.debug(self, msg, *args, **kwargs)

    @classmethod
    def logger(cls):
        logging.setLoggerClass(cls)
        debug_logger = logging.getLogger('sidecar')
        logging.setLoggerClass(logging.Logger)
        return debug_logger

log = DebugLogger.logger()
