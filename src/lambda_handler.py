#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''\
AWS Lambda handler example application.
'''

import sys

from get_parameter import get_parameter


def lambda_handler(event, context): # pylint: disable=unused-argument
	'''\
	Implement example function to test the AWS Lambda handler.

	This function exist only for tests presupposes, some code here is
	used only as examples.
	'''
	### Load Parameter Store values from extension
	OPENAI_API_KEY=get_parameter(
		'OPENAI_API_KEY'
	)
	#print(f'Found config values: {parameter_value}')

	#return f'Hello from AWS Lambda using Python {sys.version}!!! {parameter_value}'
	return f'Hello from AWS Lambda using Python {sys.version}!!!'

# vim: nu ts=4 fdm=indent noet ft=python:
