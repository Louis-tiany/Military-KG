import time
from logging import log
import re
from loguru import logger
import os

from numpy.core.defchararray import replace
from py2neo import data
from Neo4jDataBase import Neo4jDataBase
from pykeen_transe import *
import sys
import json


from flask import Flask, jsonify, request
from flask_cors import CORS

from neo4j import GraphDatabase

from utils import entity_resolve

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, supports_credentials=True)

logger.add(sys.stdout, format="{time} - {level} - {message}", filter="sub.module")


database = Neo4jDataBase()

# @app.route('/app')
def index():
    radar = "ACR 6"
    platformName = predRadarCarryRela(radar)
    nodes, links = database.GetWeaponRadar(platformName)
    logger.info(nodes)
    logger.info(links)
    
    logger.info(platformName)
    # return jsonify(triples)


@app.route('/searchOneNode', methods = ['POST'])
def searchOneNode():
    nodeId = request.get_json()['nodeId']
    nodeName = database.searchNodeById(nodeId)
    nodes, links = database.nodeInfo(nodeName)
    return jsonify({'nodes': nodes, 'links': links})


@app.route('/initial')
def initial():
    return jsonify({'group': '4', 'name': '德国戴勒姆-本茨宇航公司(DASA)', 'year': '1000'}, {'group': '4', 'name': '福特级航母', 'year': '100000'})


@app.route('/data')
def getJsonData():
    database = Neo4jDataBase()
    # nodes, links = database.GetWeaponRadar("歼-11战斗机")
    # nodes, links = 
    return jsonify(database.getJson())

@app.route('/query', methods = ['POST'])
def query():
    obj = request.get_json()['obj']
    logger.info(obj)
    nodes, links = database.query(obj)
    return jsonify({'nodes': nodes, 'links': links})






def main():
    database = Neo4jDataBase()
    platformName = predRadarCarryRela("ACR 6")
    triples = database.GetWeaponRadar(platformName)
    logger.info(triples)


if __name__ == '__main__':
    # start = time.clock()
    # index()
    # end = time.clock()
    # logger.info("智能推理耗时为：%s s"% (end - start))

        # print(type(item))
        # print(item.values('n'))
        # node = item.values('n')[0]
        # print(type(node))
        # print(list(node.labels)[0])
        # print(type(node.labels))
        # print(dict(node))

        # break
    
    app.run(debug = True, port = 8000)