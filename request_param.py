#!/usr/bin/env python
# coding: utf-8
# created on 2014-03-31 19:07:37
"""
    做成类似于Spring的@RequestParam注解的decorator形式，但是现在获得的函数参数有些问题
"""

__author__ = 'wangqunwhuhb@126.com'

import inspect
import logging

def str2IntList(s):
    return map(int, s)

def request_param(method="GET", arg_offset=1, *args, **kwargs):
    """
    this decorator's function is as java spring framewrok's @RequestParam anotation
    make sure to put it adjust to the view function as it will get view's args
    """
    if len(args) > 0:
        raise ValueError("request_param cannot process args without default value")
    def __method(func):
        # get func's arg names
        argSpec = inspect.getargspec(func)
        ARG_NAME_LIST = argSpec.args
        ARG_DEFAULT_VALUE_TUPLE = argSpec.defaults
        HAS_DEFAULT_VALUE_INDEX = len(ARG_NAME_LIST) - len(ARG_DEFAULT_VALUE_TUPLE)
        def __call(*innerArgs, **innerKWargs):
            logging.debug("innerKWargs: %s ", str(innerKWargs))
            logging.debug("kwargs: %s", str(kwargs))
            logging.debug("HAS_DEFAULT_VALUE_INDEX: %d", HAS_DEFAULT_VALUE_INDEX)
            request = innerArgs[0]
            if request.method in method:
                if request.method == "GET":
                    params = request.GET
                elif request.method == "POST":
                    params = request.POST
                else:
                    raise ValueError("unsupported method %s in request_param"%(request.method))
            for i in range(arg_offset, len(ARG_NAME_LIST)):
                arg = ARG_NAME_LIST[i]
                if arg in innerKWargs:
                    logging.debug("ignore %s as it has been filled", arg)
                    continue
                convertor = kwargs.get(arg, None)
                if isinstance(convertor, tuple):
                    logging.debug("get %s using getlist method", arg)
                    value = params.getlist(arg, None)
                else:
                    value = params.get(arg, None)
                if value == None or value == []:
                    if i < HAS_DEFAULT_VALUE_INDEX:
                        msg = "%s need param"%arg
                        logging.debug(msg)
                        raise ValueError(msg)
                    else:
                        logging.debug("do not find value for arg: %s, use default value", arg)
                else:
                    #first convert string to the appropriate value if necessary
                    #convert value if its not a list
                    if convertor:
                        convertor_func = convertor if not isinstance(convertor, tuple) else convertor[0]
                        logging.debug("convertor arg: %s value: %s using %s", arg, str(value), convertor_func.__name__)
                        value = convertor_func(value)
                    innerKWargs[arg] = value
                    logging.debug("mapping param %s to value %s", arg, value)
            return func(*innerArgs, **innerKWargs)
        return __call
    return __method
