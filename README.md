# 军事装备知识图谱
马上毕业了，回顾三年还是做了很多工作，其中也参考了很多开源程序，闲来无事开一篇文章，记录一下我的毕业设计。我的毕设是做领域知识图谱，知识图谱的构建主要有一下几步：数据采集、数据处理、数据存储以及可视化。知识图谱的可视化功能是很强的，因此我根据网上基于`vue`和`d3.js`可视化程序，改造为了我的知识图谱可视化方案。

## 简介
系统的总体架构分为知识存储层和知识图谱应用层。知识图谱的知识存储层主要涉及到对数据的采集、处理得到知识三元组，然后将从数据中抽取到的军事装备知识进行存储；应用层完成对军事装备实体的查询、军事装备之间关系的查询、各个类别的军事装备信息的知识概览等功能，并通过Vue.js和D3.js应用开发技术给用户提供知识图谱的可视化及交互效果。
![架构图](https://raw.githubusercontent.com/Louis-tiany/Military-KG/main/image/%E6%9E%B6%E6%9E%84%E5%9B%BE.png)

### 数据获取
将华戍防务公司开发的墨子·未来指挥官军事推演软件数据库作为结构化数据源，同时，采用`Python`编程语言，`urllib3`、`xpath`和`re`库编写爬虫，采集环球军事网和`https://www.radartutorial.eu/`网站中的数据。
#### 墨子·未来指挥官
[墨子联合作战推演系统](http://www.hs-defense.com/)以现代海空作战推演仿真为主，覆盖陆、海、空、天、电全域联合作战，支持战术、战役级作战的推演仿真。该款软件内包含了大量的武器装备数据，按照官网安装完软件后，可以跳过权限表登录数据库，得到结构化的装备数据。
![墨子·未来指挥官](https://raw.githubusercontent.com/Louis-tiany/Military-KG/main/image/mozi.png)
#### 环球军事网·环球武器库
环球军事网·环球武器库的数据我采用了[liuhuanyong](https://github.com/liuhuanyong/QAonMilitaryKG)的数据，他做的教程质量非常高，看了他的教程和知识图谱示例可以很快地入手知识图谱，在此对这位大牛表示感谢。

#### Radartutorial
[Radartutorial网站](https://www.radartutorial.eu/)，是一个为了教育目的而创建的，为雷达专业相关学者、维护人员提供雷达原理和技术的详细概述的网站。同样的，网站中将雷达按照技术体制等进行了详尽的分类，并收录了数百个雷达的参数数据。这里我使用爬虫对该网站数据进行了爬取，爬虫程序位于`ConstructDatabases/util/radardata.py`（由于编写的时间比较早，代码可能已经无法运行了...）。
![Radartutorial](https://raw.githubusercontent.com/Louis-tiany/Military-KG/main/image/radartutorial.png)

### 数据处理
数据处理有两方面，首先以上获取到的数据存在相互关联的较少，并且大量的数据是以数据属性的形式存在的，因此针对数据属性，将其建模为类（节点），并且采用随机的方式生成一些链接，使得数据的关联性更加丰富；其次，还有大量非结构化数据，例如文本数据，这些数据需要利用知识抽取算法得到结构化的`SPO`三元组。这里我使用了哈工大的[`ltp`语言技术平台](https://ltp.ai/)对三元组进行抽取（抽取代码为`ConstructDatabases/util/triples.py`）。
![Radartutorial](https://raw.githubusercontent.com/Louis-tiany/Military-KG/main/image/ltp.png)


### 数据存储
Neo4j是目前市场上较为成熟的高性能图数据库，自带有展示界面，广泛应用在市面上的知识图谱中。本项目将所有知识存储到了该款图数据库中。推荐用`docker`安装neo4j数据库。
![Radartutorial](https://raw.githubusercontent.com/Louis-tiany/Military-KG/main/image/neo4j.png)

### 可视化系统
该可视化系统采用了`vue`框架和`d3.js`库，参考了CoderWanp的[vue-d3-graph](https://github.com/CoderWanp/vue-d3-graph)项目，感谢作者开源了功能丰富、美观的知识图谱可视化程序并且编写了详细的教程。可视化大概分为一下几个模块：

- 信息概览
在系统界面上单击鼠标左键选中节点，系统会高亮与该节点相关联的实体节点，并且在页面的右下角会弹出选中实体的知识概览信息
![Radartutorial](https://raw.githubusercontent.com/Louis-tiany/Military-KG/main/image/visualization1.png)
- 二维可视化
在左侧的文字搜索框中搜索感兴趣的节点，可以对该节点及其相邻节点高亮显示。
![Radartutorial](https://raw.githubusercontent.com/Louis-tiany/Military-KG/main/image/visualization3.png)
- 三维可视化
![Radartutorial](https://raw.githubusercontent.com/Louis-tiany/Military-KG/main/image/visualization2.png)

## 如何运行？
### neo4j数据库部署
推荐在`linux`平台安装数据库，几行命令就搞定，非常方便。使用`docker`安装neo4j数据库的教程[在这里](https://hub.docker.com/_/neo4j/)。安装好了之后，需要网页登录一下，更改数据库的用户名密码，再把程序连接neo4j数据库的密码部分更新为新密码，否则会连接失败，同时需要安装相应的`python`软件包。
### nodejs
前端可视化工程采用`vue.js`框架编写，需要[`node.js`](https://nodejs.org/en/)开发环境。然后在前端根目录`Frontend`执行`npm install`，安装好依赖包后执行`npm run serve`即可运行。
### KGServer
前端需要请求后端才能获得数据，这里需要将数据库的`ip`，用户名，密码做对应的修改。而后运行`Backend/KGServer.py`，再去刷新前端页面可以看到知识图谱的可视化效果。需要注意的是，我这里还加了模糊搜索功能，需要用到Bert等模型，这块需要增加的代码较多；如果不需要模糊匹配等功能将`Backend/Neo4jDataBase.py`中相关的程序接口注释掉即可。相关的模糊匹配计算可以参考[这个仓库](https://github.com/WenRichard/KBQA-BERT)完成相似度匹配算法，并以`HTTP`接口向外提供服务，对该系统功能进行拓展。
