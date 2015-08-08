#! /usr/bin/env python

'''
Utilities for interacting with CMAP annotations.
Provides classes to submit queries to CMAP web API and return results as common 
Python data structures.

Dave Wadden, Spring 2014
'''

from __future__ import division
import requests
import numpy as np
import pandas as pd
import os
from os import path
import urlparse
import json
from copy import copy

# global variable: the shell variable name for the API key
KEY_VARNAME = 'LINCS_API_KEY'

class CMapAPI(object):
	'''
	Class to query CMAP web API and retrieve CMAP data annotations.
	For documentation on available CMAP collections and annotations, see the
	lincscloud API documentation:
	http://api.lincscloud.org/a2/docs

	To query the web api, an API key must be given. If the Unix environment
	variable LINCS_API_KEY is set, Python by default will take the contents of 
	this file to be the API key. This behavior can be changed by specifying
	"key" or "keyfile" options below.

	Parameters
	----------
	collection : str
		CMAP collection to query. Default is "sig_info". For list of available
		collections, see documentation above or examine CMapAPI.collections

	key : str
		A user key to use when performing queries. At most one of key and
		keyfile should be supplied. If both are None, Python attempts to find
		an API key at the file given by the environment variable LINCS_API_KEY.
		If no file is found, the user is prompted to input a key.
		To obtain an API key, contact lincs@broadinstitute.org.

	keyfile : str
		The path to a file containing a user key.

	version: str
		The version of LINCS cloud API with which to connect. If not given,
		connects to LINCS default.

	return_id : bool
		By default, API records are returned with an internal field _id. This
		field is not generally useful for analysis, so by default it will not
		be returned. Setting "return_id" to True will return this field.

	verbose : bool
		If True, give more detailed error messages if API call fails. True
		by default.
	'''
	
	############################################################################
	# Variables stored on the class
	# Hard-coded list of available Mongo collections
	_collections = ['cellinfo', 'geneinfo', 'instinfo', 
				    'pertinfo', 'plateinfo', 'siginfo']	
	# map from Python arguments to API arguments
	_argsmap = {'query' : 'q',
			   'count' : 'c',
			   'distinct' : 'd',
			   'fields' : 'f',
			   'group' : 'g',
			   'limit' : 'l',
			   'sort_order' : 's',
			   'skip': 'sk'}
	# store the base URL
	_baseurl = 'http://api.lincscloud.org'
	# query fields that induce some sort of summarization of the query
	_summary_fields = ['count', 'distinct', 'group']
	# hard-code the maximum limit size for queries
	_maxlimit = 1000
	############################################################################
	
	def __init__(self, collection = 'siginfo', 
	             key = None, keyfile = None, version = None, 
	             return_id = False, verbose = True):
		self.version = version
		self.verbose = verbose
		self.return_id = return_id
		# check that collection is valid
		if not collection in self._collections:
			errorstr = ('{0} is not an available collection. Available '
			            'collections are:\n{1}')
			errorstr = errorstr.format(collection, '\n'.join(self._collections))
			raise CMapAPIException(errorstr)
		else:
			self.collection = collection

		# set the user key
		self.key = get_user_key(key, keyfile)

		# set the base url
		if self.version is None:
			self.base_url = path.join(self._baseurl, self.collection)
		else:
			self.base_url = path.join(self._baseurl, self.version, 
			                          self.collection)

	def __repr__(self):
		repstr = ('CMapAPI object.\n'
		          'Collection : {0}.\n'
		          'Base web URL: {1}.\n'
		          'API Version: {2}.')
		repstr = repstr.format(self.collection, self._baseurl,
		                       'current' if self.version is None else self.version)
		return repstr

	def find(self, 
	         query, 
	         fields = None,
	         count = None, 
	         distinct = None,
	         group = None,
	         limit = 10,
	         sort_order = None,
	         skip = None,
	         toDataFrame = False):
		'''
		Submit a query to the CMAP web API. Return results as Python data
		structure (either a list of a Pandas DataFrame). For more detail
		on query arguments, see the Lincscloud API documentation.

		The following restriction is placed on the query arguments:
		-The arguments "distinct", "count", and "group" are mutually exclusive;
			only one should be supplied. These three can be thought of as 
			"summary fields" because they request a summary of the query to 
			be returned.

		Parameters
		----------
		query : dict
			A Python dictionary specifying the query. The syntax directly mimics
			the syntax for PyMongo, detailed here:
			http://api.mongodb.org/python/current/.
			For more on Mongo query syntax in general, see the Mongo website:
			http://docs.mongodb.org/manual/tutorial/query-documents/

		fields : list or dict
			Specify the fields to be returned from the query.
			If list, lists the fields to be returned.
			If dict, values of True specify the field to be returned.

		count : bool
			If True, return the result count for the query.

		distinct : str
			The input, if given, must be a database field. A list of distinct
			values for the specified field is returned.

		group : str
			The input, if given, must be a database field. The query returns
			the counts of the result, split by the unique values of the
			specified field.

		limit : int
			If given, a limit on the number of results to return. Default is 10.
			The API limits the number of records that may be requested at once.

		sort_order : dict
			If given, specifies the order in which to sort the query results.
			Keys should be databse fields; values should be either 1 for
			ascending sort or -1 for descending sort.

		skip : int
			If given, skip the specified number of results.

		toDataFrame : bool
			If True, convert query result to Pandas DataFrame (or Series if
			"distinct" is supplied). This option must be False if "count" is
			True.
		'''
		# assemble dictionary of query arguments, validate arguments
		query_args = {}
		for key in self._argsmap: query_args[key] = eval(key)
		is_summary = self._validate_args(query_args)

		# get count; warn user if no matches or matches are greater than limit
		res_count = self.get_count(query_args)
		if count:
			return res_count
		else:
			if not res_count:
				errstr = 'Query has no matches.'
				print errstr
				return
		if not is_summary:
			if self.verbose:
				if (res_count > limit):
					errstr = ('{0} records match query, but the limit is {1}.\n' +
							  'First {1} entries will be returned.\n')
					errstr = errstr.format(res_count, limit)
					print errstr

		# run the regular query, return
		res = self.request(query_args, toDataFrame)
		return res

	def get_count(self, query_args):
		'''
		Count the number of entries matching the query.

		Paratmers
		---------
		query_args : dict
			The dictionary of arguments for the query.
		'''
		count_query_args = {'query' : query_args['query'], 'count' : True}
		return self.request(count_query_args, toDataFrame = False)

	def request(self, query_args, toDataFrame):
		'''
		Make a request to the server given query arguments in a dictionary.
		Returns the result.

		Parameters
		----------
		query_args : dict
			The dictionary of query arguments to be converted to html and
			submitted to the API.

		toDataFrame : bool
			Indicates whether the result should be converted to a Pandas object.
		'''
		req = self._generate_request(query_args)
		q = requests.get(self.base_url, params = req)
		res = self._parse_results(q, query_args, toDataFrame)
		return res

	def _validate_args(self, query_args):
		'''
		Private method to validate arguments
		'''
		# check that at most one of the summary fields was supplied
		summary_fields = [x for x in self._summary_fields 
						  if query_args[x] is not None]
		nsummary = len(summary_fields)
		if nsummary > 1:
			errstr = ('At most 1 summary field should be supplied.\n' +
			          'The summary fields are:\n' +
			          '\n'.join(self._summary_fields))
			raise CMapAPIException(errstr)
		if (query_args['limit'] > self._maxlimit) and (not nsummary):
			errstr = ('API limit is {0}.\n'
			          'If more than {0} records match query, loop using the "skip" parameter.')
			errstr = errstr.format(self._maxlimit)
			raise CMapAPIException(errstr)
		# return whether or not a summary has been requested
		return bool(nsummary)

	def _generate_request(self, query_args):
		'''
		Private method to generate a request from the query arguments
		'''
		req = {}
		for key, thisarg in query_args.items():
			if thisarg is not None:
				req[self._argsmap[key]] = self._format_args(key, thisarg)
			else:
				if (key == 'fields') and (not self.return_id):
					req[self._argsmap[key]] = json.dumps({'_id' : 0})
		req['user_key'] = self.key
		return req

	def _format_args(self, key, thisarg):
		'''
		Helper function for _generate_request; formats arguments for the API call.
		'''
		if key == 'fields':
			if type(thisarg) is list:
				thisarg = dict.fromkeys(thisarg, 1)
			if not self.return_id:
				thisarg['_id'] = 0
			res = json.dumps(thisarg)
		elif key in ['query', 'sort_order', 'count']:
			res = json.dumps(thisarg)
		else:
			res = thisarg
		return res

	def _parse_results(self, q, query_args, toDataFrame):
		'''
		Parse results from API call.
		'''
		# check from errors with the API call
		if not q.ok:
			errstr = ('The API call returned an error. The reason given was:\n\n'
			            + q.reason)
			if self.verbose:
				errstr = errstr + '\n\nThe full error message was:\n\n' + q.content
			raise CMapAPIException(errstr)
		# if it's good, get the results
		res = q.json()
		# check if on of the summary fields is set
		if query_args['count']:
			return res['count']
		elif query_args['distinct'] is not None:
			if toDataFrame: return pd.Series(res).order().reset_index(drop = True)
		elif query_args['group'] is not None:
			if toDataFrame:
				res = pd.DataFrame(res).set_index('_id')
				res.index.name = query_args['group']
			return res
		# if not, see if there's just one field
		else:
			# if just one field, first check if any of the returned documents are None, 
			# meaning they didn't contain the one requested field
			if len(query_args['fields']) == 1:
				if any([not(x) for x in res]):
					res = [x for x in res if x]
					if self.verbose:
						print 'only {0} documents contained the one requested field'.format(len(res))
			# Check that all requested fields were found
			if query_args['fields'] is not None:
				missings = self._check_fields(res, query_args['fields'])
				# if single field, output list / series
				if (len(query_args['fields']) == 1) and (not missings):
					field = query_args['fields'][0]
					if toDataFrame:
						res = pd.DataFrame(res)[field]
					else:
						res = [x[field] for x in res if x]
					return res
			# if more fields, convert to data frame
			if toDataFrame: res = pd.DataFrame(res)
		return res

	def _check_fields(self, res, fields):
		'''
		Check that all requested fields were returned in the query result.
		'''
		allfields = sorted(set([z for y in [x.keys() for x in res if x] 
		                   		for z in y]))
		missings = sorted(np.setdiff1d(fields, allfields))
		if missings:
			errstr = ('The following requested fields were not found ' +
			          'in any documents:\n' +
			          '\n'.join(missings))
			print errstr
		# if verbose is set, notify if some fields were not found in all docs
		if self.verbose:
			indiv_missing = [np.setdiff1d(allfields, x.keys())
							 for x in res if x]
			indiv_missing = sorted(set([z for y in indiv_missing 
			                       		for z in y]))
			if indiv_missing:
				errstr = ('The following requested fields were found ' +
				          'in some, but not all, documents:\n' +
				          '\n'.join(indiv_missing))
				print errstr
		return missings

class APIContainer(object):
	'''
	Convenience class to wrap a number of CMapAPI instances set up to query
	different collections.

	Parameters
	----------
	collections : list
		A CMapAPI object is generated for each collection in the list. These
		objects are accessed as attributes of the APIContainer object. If no
		input is given, a default list of collections is used.

	The arguments below are each passed the individual CMapAPI instances
	upon initialization:
	key
	keyfile
	version
	return_id
	verbose
	'''

	############################################################################
	# default collection stored on the class
	_dflt_collections = ['cellinfo', 'geneinfo', 'instinfo',
						 'pertinfo', 'plateinfo', 'siginfo']
	############################################################################

	def __init__(self, collections = None, key = None, keyfile = None,
	             version = None, return_id = None, verbose = True):
		if collections is None:
			self.collections = self._dflt_collections
		else:
			self.collections = collections
		# get the key, pass it to all collections in turn
		self.key = get_user_key(key, keyfile)
		for collection in self.collections:
			setattr(self, collection, CMapAPI(collection, self.key, 
			        						  None, version, 
			        						  return_id, verbose))

	def __repr__(self):
		repstr = ('APIContainer object.\n' +
		          'Contains the following collections:\n' +
		          '\n'.join(self.collections))
		return repstr

def get_user_key(key = None, keyfile = None):
	'''
	Function to get user's CMAP API key; called by both CMapAPI and APIContainer.
	If neither key nor keyfile is given, Python looks for the key in the file
	given by the shell variable defined by the global KEY_VARNAME. If no such
	file is present, the user is prompted for input.

	Alternately, the user may enter the key directly as a string via the 'key'
	variable, or as a path to the file containing the key via the 'keyfile'
	variable.

	Parameters
	----------
	key : str
		The user key.

	keyfile : str
		Path to a file containing the user key.
	'''
	# check that only 1 argument is given
	if (key is not None) and (keyfile is not None):
		errorstr = ('Arguments should be supplied for at most one '
		            'of "key" and "keyfile".')
		raise CMapAPIException(errorstr)
	# if the key is given, use it
	if key is not None: 
		res = key
	# if there's a keyfile, us it
	elif keyfile is not None:
		with open(keyfile, 'r') as f:
			res = f.read()
	# otherwise check the environment
	elif KEY_VARNAME in os.environ.keys():
		with open(os.environ[KEY_VARNAME]) as f:
			res = f.read()
	# if it's not there, ask user for input
	else:
		res = raw_input('Please enter API key\n')
	return res

class CMapAPIException(Exception):
	'''
	Base class for all excpetions related to CMAP API
	'''
	pass
