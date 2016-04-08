#!/usr/bin/env python
import py2neo
from py2neo.packages.httpstream import http
from py2neo.cypher import cypher_escape
from multiprocessing import Pool

import httplib

import csv
import logging
import argparse
import sys
from pprint import pprint

httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

parser = argparse.ArgumentParser()
parser.add_argument("info",
                    help="The info file")

opts=parser.parse_args()

logging.basicConfig(level=logging.ERROR)

http.socket_timeout = 9999

numiter = 1000

graph = py2neo.Graph()
graph.bind("http://localhost:7474/db/data/")

label = "MOL"

idxout = graph.cypher.execute("CREATE CONSTRAINT ON (n:"+label+") ASSERT n.id IS UNIQUE")

def process_statement( statements ):
    
    tx = graph.cypher.begin()

    #print statements
    logging.info('proc sent')

    for statement in statements:
        #print statement
        tx.append(statement)

    tx.process()
    tx.commit()


poolnum = 7;

p = Pool(poolnum)

def create_molid(line, number):
	molid = str(line[0]).strip()
	name = str(line[2]).strip()
	moltype = str(line[4]).strip()
	name = name.replace("\\", "\\\\")
	name = name.replace("\"", "\\\"")
					

	# We assume always al params
	statement = "CREATE (n:"+label+" { id:\""+molid+"\", name:\""+name+"\", type:\""+moltype+"\" })"
	#print statement
		
	return statement

def create_relation( line, number):
	
	
	return statement


logging.info('storing name info')
reader =  csv.reader(open(opts.info),delimiter="\t")

iter = 0

list_statements =  []
statements = []

for row in reader:
	
	if row[0].startswith( '!' ):
		continue
	
	statement = create_molid(row, iter)
	statements.append( statement )
	iter = iter + 1
	if ( iter > numiter ):
		list_statements.append( statements )
		iter = 0
		statements = []

list_statements.append( statements )
res = p.map( process_statement, list_statements )

idxout = graph.cypher.execute("CREATE INDEX ON :"+label+"(type)")
idxout = graph.cypher.execute("CREATE INDEX ON :"+label+"(name)")
