from logging import getLoggerClass
from matplotlib.pyplot import get
from py2neo import *
import os
from loguru import logger
from py2neo import cypher
from py2neo.database import Graph
from py2neo.integration.pandas import cursor_to_data_frame
from pykeen import triples
from torch import cudnn_affine_grid_generator
import tqdm
import sys
import json
import re
from utils import entity_resolve

logger.add(sys.stdout, format="{time} - {level} - {message}", filter="sub.module")

num = 100
class Neo4jDataBase():
    def __init__(self) -> None:
        # self.num = 500
        self.graph_ = Graph(host = "192.168.192.130", auth = ('neo4j', '123456'))
        self.nodeMatcher = NodeMatcher(self.graph_)
        self.relaMather = RelationshipMatcher(self.graph_)
        logger.add(sys.stdout, format="{time} - {level} - {message}", filter="sub.module")
    def _runCypher(self, cypherStr) -> list:
        response = self.graph_.run(cypherStr)
        return [item.values('n')[0] for item in response]

    def searchNode(self):
        cypher = "match (n) return n limit " + str(num)
        nodes = self._runCypher(cypherStr = cypher)
        ids = [node.identity for node in nodes]
        labels = [list(node.labels)[0] for node in nodes]
        properties = [dict(node) for node in nodes]
        # logger.info(labels[0])
        # logger.info(properties[12030])
        # logger.info(nodes[100].identity)

        return ids, labels, properties
        
    def searchRela(self):
        cypher = "MATCH n=()-[]->() RETURN n limit " + str(num)
        paths = self._runCypher(cypherStr = cypher)
        logger.info((paths[0].start_node.identity))
        startId = [path.start_node.identity for path in paths]
        endId = [path.end_node.identity for path in paths]
        labels = [list(path.types())[0] for path in paths]
        properties = [{} for i in range(len(labels))]
        return startId, endId, labels, properties

    def getJson(self):
        ids, labels, properties = self.searchNode()
        startId, endId, linkLabels, linkProperties = self.searchRela()
        logger.info(len(startId))
        
        nodes = [{'id': id, 'label': label, 'properties': property} for id, label, property in zip(ids, labels, properties)]
        links = [{'source': start, 'target': end, 'type': label, 'properties': linkProperty} for start, end, label, linkProperty in zip(startId, endId, linkLabels, linkProperties)]

        logger.info(nodes)
        logger.info(links)
        
        return {'nodes': nodes, 'links': links}

        


    def searchNodeById(self, id: int) -> str:
        cypher = "MATCH (node) WHERE id(node) = %d RETURN node" % id
        cursor = self.graph_.run(cypher= cypher)
        # logger.info(next(cursor)['node']['name'])
        return next(cursor)['node']['name']
        pass


    #获取雷达可能搭载的平台，而后查询平台上搭载的所有雷达及所有信息
    def _getNodeLabels(self):
        relations =  [rela for rela in self.graph_.schema.node_labels]
        return relations
    def _getRelaLabels(self):
        nodes = [rela for rela in self.graph_.schema.relationship_types]
        return nodes

    def nodeInfo(self, nodeName):
        nodeLabel = self._getNodeLabels()
        relationTypes = self._getRelaLabels()
        logger.info(nodeLabel)
        logger.info(relationTypes)
        
        cypher = "match (m)-[r]-(n) where m.name='%s' return m,r,n" % (nodeName)
        # print(cypher)
        res = self.graph_.run(cypher= cypher)
        triplesDict = {}
        nodes = []
        links = []
        # items = re.match(r"[(](.*)[)]-\[:([^\[\]]*) {}\]->[(](.*)[)]", triple, re.I | re.M)
        for item in res:
            startNode = item['m']
            endNode = item['n']

            startId = startNode.identity
            endId = endNode.identity
            S = str(item['m']['name'])
            logger.info((item)['m']['name'])
            rela = re.match(r"[(](.*)[)]-\[:([^\[\]]*) {}\]->[(](.*)[)]", str(item['r']), re.I|re.M).group(2)
            P = str(rela)
            O = str(item['m']['name'])

            nodes.append({'id': startId, 'label': str(startNode.labels), 'properties': dict(startNode)})
            nodes.append({'id': endId, 'label': str(endNode.labels), 'properties': dict(endNode)})
            links.append({'source': startId, 'target': endId, 'type': P, 'propertities': {}})

            logger.info("S: %s P: %s O: %s" %(S, P, O))
            logger.info(rela)
            logger.info(((item)['r']))
            logger.info(dict((item)['m']))
        logger.info("nodes: %s" % str(nodes))
        logger.info("links: %s" % str(links))
        return nodes, links
    
    def count(self):
        cypher = "MATCH (n) RETURN count(*)"
        # print(cypher)
        nodeNum = self.graph_.run(cypher= cypher)
        logger.info(nodeNum)
        cypher = "MATCH (n)-[r]->() RETURN COUNT(r)"
        relaNum = self.graph_.run(cypher= cypher)
        logger.info(self.graph_.run(cypher= cypher))


    def query(self, obj):
        nodeLabel = self._getNodeLabels()
        relationTypes = self._getRelaLabels()

        if obj in relationTypes:
            logger.info("rela")
            return self.getRelationship(obj)
        else:
            logger.info("entity")
            entity = entity_resolve(obj)
            logger.info(entity)
            database = Neo4jDataBase()
            nodes, links = database.GetWeaponRadar(entity)
            # nodes, links = database.GetWeaponRadar("前卫-1M(QW-1M)便携式防空导弹系统")
            return nodes, links


    def getRelationship(self, relationship):
        nodeLabel = self._getNodeLabels()
        relationTypes = self._getRelaLabels()
        cypher = "match (m)-[r:`%s`]-(n) return m,r,n" % (relationship)
        res = self.graph_.run(cypher= cypher)
        # logger.info(res)
        triplesDict = {}
        nodes = []
        links = []

        for item in res:
            startNode = item['m']
            endNode = item['n']

            startId = startNode.identity
            endId = endNode.identity
            S = str(item['m']['name'])
            # logger.info((item)['m']['name'])
            rela = re.match(r"[(](.*)[)]-\[:([^\[\]]*) {}\]->[(](.*)[)]", str(item['r']), re.I|re.M).group(2)
            P = str(rela)
            O = str(item['m']['name'])

            nodes.append({'id': startId, 'label': str(startNode.labels), 'properties': dict(startNode)})
            nodes.append({'id': endId, 'label': str(endNode.labels), 'properties': dict(endNode)})
            links.append({'source': startId, 'target': endId, 'type': P, 'propertities': {}})

            if len(nodes) > 300 and len(links) > 500:
                break

            # logger.info("S: %s P: %s O: %s" %(S, P, O))
            # logger.info(rela)
            # logger.info(((item)['r']))
            # logger.info(dict((item)['m']))
        logger.info("nodes: %s" % str(nodes))
        logger.info("links: %s" % str(links))
        nodes = nodes[0:500]
        links = links[0:500]
        return nodes, links



    def GetWeaponRadar(self, platformName):
        nodeLabel = self._getNodeLabels()
        relationTypes = self._getRelaLabels()
        
        cypher = "match (m)-[r]-(n) where m.name='%s' return m,r,n" % (platformName)
        # print(cypher)
        res = self.graph_.run(cypher= cypher)
        triplesDict = {}
        nodes = []
        links = []
        # items = re.match(r"[(](.*)[)]-\[:([^\[\]]*) {}\]->[(](.*)[)]", triple, re.I | re.M)
        for item in res:
            startNode = item['m']
            endNode = item['n']

            startId = startNode.identity
            endId = endNode.identity
            S = str(item['m']['name'])
            # logger.info((item)['m']['name'])
            rela = re.match(r"[(](.*)[)]-\[:([^\[\]]*) {}\]->[(](.*)[)]", str(item['r']), re.I|re.M).group(2)
            P = str(rela)
            O = str(item['m']['name'])

            nodes.append({'id': startId, 'label': str(startNode.labels), 'properties': dict(startNode)})
            nodes.append({'id': endId, 'label': str(endNode.labels), 'properties': dict(endNode)})
            links.append({'source': startId, 'target': endId, 'type': P, 'propertities': {}})

            # logger.info("S: %s P: %s O: %s" %(S, P, O))
            # logger.info(rela)
            # logger.info(((item)['r']))
            # logger.info(dict((item)['m']))
        logger.info("nodes: %s" % str(nodes))
        logger.info("links: %s" % str(links))
        return nodes, links



        #慢速代码
        #获取平台节点
        for label in tqdm.tqdm(nodeLabel):
            node = self.nodeMatcher.match(label, name = platformName).first()
            if node:
                break

        triplesDict = {}
        #速度慢，遍历全图搜索
        for rela in tqdm.tqdm(relationTypes):
            triples = []
            for triple in self.graph_.match(r_type = rela):
                record = tuple()
                if triple.start_node['name'] == node['name'] or triple.end_node['name'] == node['name']:
                    triple = str(triple)
                    items = re.match(r"[(](.*)[)]-\[:([^\[\]]*) {}\]->[(](.*)[)]", triple, re.I | re.M)
                    #logger.info(items.group(1))
                    #logger.info(items.group(2))
                    #logger.info(items.group(3))
                    record = (items.group(1), items.group(2), items.group(3))
                    if record:
                        triples.append(record)

            if triples:
                triplesDict[rela] = triples

        return triplesDict





if __name__ == '__main__':
    database = Neo4jDataBase()
    # triples = database.GetWeaponRadar("履带式")
    # logger.info(triples)
    # database.searchNode()
    # database.searchRela()
    # print(json.dumps(database.getJson(), ensure_ascii = False))
    # database.GetWeaponRadar(platformName="前卫-1M(QW-1M)便携式防空导弹系统")

    # database.searchNodeById(19)
    # database.GetWeaponRadar("前卫-1M(QW-1M)便携式防空导弹系统")
    database.nodeInfo("前卫-1M(QW-1M)便携式防空导弹系统")
    # database.getRelationship("研发")
    database.count()