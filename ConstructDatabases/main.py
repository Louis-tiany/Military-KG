import os
import json
from py2neo import *
import time
import tqdm
from loguru import logger
from random import choice
import random
import sys
import re
import csv

logger.add(sys.stdout, format="{time} - {level} - {message}", filter="sub.module")


class KnowledgeGraph():
    def __init__(self):
        self.graph_ = Graph(host = "192.168.192.130", port = 7687, auth = ('neo4j', '123456'))
        self.matcher = NodeMatcher(self.graph_)

        self.militaryPath_ = r"data\military.json"
        self.nodeLabels_ = ['气动布局', '生产单位', '研发单位','动力装置', '发动机', '产国', '飞行速度', '底盘类型', '发动机数量', '制造商']


        self.radarPath_ = r"data\radarData.json"

    def deleteAll(self):
        self.graph_.delete_all()
        logger.info("delete all")
        logger.info("========================================================================================================")


    def _createNode(self, label, nodeName):
        if self.findNode(label, nodeName):
            return
        else:
            node = Node(label, name = nodeName)
            self.graph_.create(node)

    def _createRelation(self, headLabel, headName, tailLabel, tailName, relation):
        try:
            head = self.findNode(headLabel, headName)
            tail = self.findNode(tailLabel, tailName)
            rela = Relationship(head, relation, tail)
            self.graph_.create(rela)
            #logger.info("create rela")
            
        except:
            #logger.warning("create ralation error")
            pass

    def _createRelationUtil(self, data, headLabel, headName, tailLabel, tailName, relation):
        try:
            self._createRelation(headLabel = headLabel, headName = data[headLabel], tailLabel = tailLabel, tailName = data[tailLabel], relation = relation)
        except:
            #logger.warning("have not label")
            pass

    def findNode(self, label, nodeName):
        node = self.matcher.match(label, name = nodeName).first()
        return node

    def info(self):
        logger.info("Node labels")
        logger.info(self.graph_.schema.node_labels)       # 查看图结构中节点标签的类别，返回结果是一个frozenset
        logger.info("Relation labels")
        logger.info(self.graph_.schema.relationship_types)       # 查看图结构中节点标签的类别，返回结果是一个frozenset
        logger.info(("========================================================================================================"))
    
        
    def readMilitaryData(self):
        with open(self.militaryPath_, 'r', encoding = 'utf-8') as file : 
            lines = file.readlines()
            for line in tqdm.tqdm(lines, desc= "Processing Military Data"):
                data = json.loads(line)
                try:
                     self._createNode(data['类型'], data['名称'])
                except:
                     pass

                for label in self.nodeLabels_:
                    try:
                        self._createNode(label, data[label])
                    except:
                        pass
                for key in data:
                    if key not in self.nodeLabels_ and key != "_id" and key != "图片":
                        node = self.findNode(data['类型'], data['名称'])
                        node[key] = data[key]
                        self.graph_.push(node)
                
                try:
                    self._createRelation(data['类型'], data['名称'], '产国', data['产国'], '属于')
                except:
                    pass
                try:
                    self._createRelation(data['类型'], data['名称'], '飞行速度', data['飞行速度'], '飞行速度')
                except:
                    pass
                try:
                    self._createRelation(data['类型'], data['名称'], '气动布局', data['气动布局'], '气动布局')
                except:
                    pass
                try:
                    self._createRelation(data['类型'], data['名称'], '气动布局', data['气动布局'], '气动布局')
                except:
                    pass
                try:
                    self._createRelation('生产单位', data['生产单位'], data['类型'], data['名称'], '生产')
                except:
                    pass
                try:
                    self._createRelation('研发单位', data['研发单位'], data['类型'], data['名称'], '研发')
                except:
                    pass
                try:
                    self._createRelation(data['类型'], data['名称'], '动力装置', data['动力装置'], '动力装置')
                except:
                    pass
                try:
                    self._createRelation(data['类型'], data['名称'], '发动机', data['发动机'], '发动机')
                except:
                    pass
                try:
                    self._createRelation(data['类型'], data['名称'], '底盘类型', data['底盘类型'], '底盘类型')
                except:
                    pass
                try:
                    self._createRelation(data['类型'], data['名称'], '发动机数量', data['发动机数量'], '发动机数量')
                except:
                    pass

                self._createRelationUtil(data, headLabel = "制造商", headName = "制造商", tailLabel = "产国", tailName = "产国", relation = "属于")
                self._createRelationUtil(data, headLabel = "生产单位", headName = "生产单位", tailLabel = "产国", tailName = "产国", relation = "属于")


    def readRadarData(self):
        with open(self.radarPath_, 'r', encoding = 'utf-8') as file : 
            lines = file.readlines()
            for line in tqdm.tqdm(lines, desc = "Processing Radar Data"):
                data = json.loads(line)
                try:
                    self._createNode("雷达", data['type'])
                    for key in data:
                        if key == 'type':
                            continue
                        else:
                            node = self.findNode("雷达", data['type'])
                            node[key] = data[key]
                            self.graph_.push(node)
                except:
                    pass
    
    def _createRela(self, startNode, relation, endNode):
        rela = Relationship(startNode, relation, endNode)
        self.graph_.create(rela)

    def createRelaWithRadar(self):
        with open(self.militaryPath_, 'r', encoding = 'utf-8') as file : 
            lines = file.readlines()
            weaponType = []
            for line in tqdm.tqdm(lines, desc = "processing military data"):
                data = json.loads(line)
                try:
                    weaponType.append(data['类型'])
                except:
                    pass
                
        #all radar node
        radars = []
        for radar in self.matcher.match("雷达"):
            radars.append(radar)
        radars = list(set(radars))

        weaponType = list(set(weaponType))
        for label in tqdm.tqdm(weaponType, desc = "insert relation between radar and weapon"):
            for weapon in self.matcher.match(label):
                self._createRela(weapon, "搭载", choice(radars))

    def exportData(self):
        file = open("data/export/exportData.csv", "w", encoding='utf8',newline='')
        writer = csv.writer(file, delimiter = '#')
        
        relation_matcher = RelationshipMatcher(graph.graph_)
        relations = [rela for rela in graph.graph_.schema.relationship_types]
        logger.info("relations")
        logger.info(relations)
        for relation in  tqdm.tqdm(relations, desc = "writing file"):
            for triple in tqdm.tqdm(relation_matcher.match(r_type = relation)):
                # logger.info(triple)
                triple = str(triple)
                items = re.match(r"[(](.*)[)]-\[([^\[\]]*)\]->[(](.*)[)]", triple, re.I | re.M)

                head = items.group(1)
                tail = items.group(3)

                writer.writerow([head, relation, tail])

        file.close()

    def createPRIType(self):
        with open(r"data/json/PRIType.json", "r", encoding = 'utf-8') as file:
            lines = file.readlines()

        for line in tqdm.tqdm(lines, desc = "insert pri data: "):
            data = json.loads(line)
            self._createNode("PRI类型", data['name'])

    def createPRIRelaWithRadar(self):
        matcher = NodeMatcher(self.graph_)
        radars = [node for node in matcher.match('雷达')]            
        PRITypes = [pri for pri in matcher.match('PRI类型')]
        for radar in tqdm.tqdm(radars):
            for i in range(random.randint(1, 3)):
                self._createRela(radar, "PRI类型", choice(PRITypes))
    def _createRadarRela(self, label, relation):
        matcher = NodeMatcher(self.graph_)
        radars = [node for node in matcher.match('雷达')]            
        Types = [Type for Type in matcher.match(label)]
        for radar in tqdm.tqdm(radars, desc = 'insert data with radar: '):
            for i in range(random.randint(1, 3)):
                self._createRela(radar, relation, choice(Types))


    def createTechSysType(self):
        with open(r"data/json/TechnicalSystemType.json", "r", encoding = 'utf-8') as file:
            lines = file.readlines()

        for line in tqdm.tqdm(lines, desc = "insert pri data: "):
            data = json.loads(line)
            self._createNode("技术体制", data['name'])
        self._createRadarRela("技术体制", "技术体制")

    
    def createAntennaScanningType(self):
        with open(r"data\json\AntennaScanningType.json", "r", encoding = 'utf-8') as file:
            lines = file.readlines()

        for line in tqdm.tqdm(lines, desc = "insert pri data: "):
            data = json.loads(line)
            self._createNode("天线扫描方式", data['name'])
        self._createRadarRela("天线扫描方式", "天线扫描方式")

    def createPWType(self):
        with open(r"data\json\PWType.json", "r", encoding = 'utf-8') as file:
            lines = file.readlines()

        for line in tqdm.tqdm(lines, desc = "insert pri data: "):
            data = json.loads(line)
            self._createNode("脉宽类型", data['name'])
        self._createRadarRela("脉宽类型", "脉宽类型")
    def createPulseModeType(self):
        with open(r"data\json\PulseModeType.json", "r", encoding = 'utf-8') as file:
            lines = file.readlines()

        for line in tqdm.tqdm(lines, desc = "insert pri data: "):
            data = json.loads(line)
            self._createNode("脉内调制类型", data['name'])
        self._createRadarRela("脉内调制类型", "脉内调制类型")
    def createPolarizationType(self):
        with open(r"data\json\PolarizationType.json", "r", encoding = 'utf-8') as file:
            lines = file.readlines()

        for line in tqdm.tqdm(lines, desc = "insert pri data: "):
            data = json.loads(line)
            self._createNode("极化类型", data['name'])
        self._createRadarRela("极化类型", "极化类型")

    def readMoziData(self):
        matcher = NodeMatcher(self.graph_)
        nations = []
        def readMoziAircraftData(self):
            nations = [node['name'] for node in matcher.match('产国')]            
            with open(r"data\Mozi\MoziAircraftData.json", 'r', encoding = 'utf-8') as file:
                lines = file.readlines()
            for line in tqdm.tqdm(lines):
                data = json.loads(line)
                self._createNode("战机", data['Name'])

                if data['enumoperatorcountryDes'] not in nations:
                    self._createNode("产国", data['enumoperatorcountryDes'])

                self._createRelation("战机", data['Name'], "产国", data['enumoperatorcountryDes'], "属于")

        def readMoziRadarData(self):
            nations = [node['name'] for node in matcher.match('产国')]            
            with open(r"data\Mozi\MoziRadarData.json", 'r', encoding = 'utf-8') as file:
                lines = file.readlines()
            for line in tqdm.tqdm(lines):
                data = json.loads(line)
                self._createNode("雷达", data['Name'])
                if data['numoperatorcountryDescription'] not in nations:
                    self._createNode("产国", data['numoperatorcountryDescription'])
                try:
                    self._createRelation("雷达", data['Name'], "产国", data['numoperatorcountryDescription', "属于"])
                except:
                    pass

        def readMoziShipData(self):
            nations = [node['name'] for node in matcher.match('产国')]            
            with open(r"data\Mozi\MoziShipData.json", 'r', encoding = 'utf-8') as file:
                lines = file.readlines()
            for line in tqdm.tqdm(lines):
                data = json.loads(line)
                self._createNode("战舰", data['Name'])
                if data['coubtryDescription'] not in nations:
                    self._createNode("产国", data['coubtryDescription'])
                try:
                    self._createRelation("战舰", data['Name'], "产国", data['coubtryDescription'], "属于")
                except:
                    pass

        def readMoziWeaponData(self):
            nations = [node['name'] for node in matcher.match('产国')]            
            with open(r"data\Mozi\MoziWeaponData.json", 'r', encoding = 'utf-8') as file:
                lines = file.readlines()
            for line in tqdm.tqdm(lines):
                data = json.loads(line)
                self._createNode(data['typeDescription'], data['Name'])
                logger.info(data)
                if data['countyrDescription'] not in nations:
                    self._createNode("产国", data['countyrComment'])
                try:
                    self._createRelation("战舰", data['Name'], "产国", data['typeDescription'], "属于")
                except:
                    pass

        readMoziAircraftData(self)
        readMoziRadarData(self)
        readMoziShipData(self)
        readMoziWeaponData(self)

def createRadarAttr(graph):
    graph.createPRIType()
    graph.createPRIRelaWithRadar()
    graph.createTechSysType()
    graph.createAntennaScanningType()
    graph.createPWType()
    graph.createPulseModeType()
    graph.createPolarizationType()


def constructDataBase(graph):
    graph = KnowledgeGraph()
    graph.deleteAll()
    graph.readMilitaryData()
    graph.readRadarData()
    graph.createRelaWithRadar()
    createRadarAttr(graph)

    graph.readMoziData()


if __name__ == '__main__':
    logger.info("insert data")
    logger.info(
        ("========================================================================================================"))
    graph = KnowledgeGraph()
    
    graph.info()
    constructDataBase(graph)
    