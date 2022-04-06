from base64 import encode
import json
from re import S
from tkinter.ttk import Sizegrip
from loguru import logger
from matplotlib.font_manager import FontProperties
import pykeen as pk
import pandas as pd
import os
from pykeen.triples import TriplesFactory
from pykeen.pipeline import pipeline
from sklearn import model_selection
import torch
from numpy import *
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from wordcloud import WordCloud
from sklearn.utils import shuffle
from py2neo import *
import numpy as np
import matplotlib
import seaborn as sns
from pykeen.models import TransE
import sys
logger.add(sys.stdout, format="{time} - {level} - {message}", filter="sub.module")

plt.rcParams['font.sans-serif']=['YaHei Consolas Hybrid'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

fontx = FontProperties(fname = r"C:\Users\tianyong\AppData\Local\Microsoft\Windows\Fonts\YaHei_Consolas_Hybrid_1.12.ttf")




def csv2tsv():
    path='./simp.csv'

    with open(path,encoding='utf-8') as f:
        data=f.read().replace('	 ','-')

    data=data.replace(',','\t')

    with open('tsv_file.txt','w',encoding='UTF-8') as f:
        f.write(data)

def train():
    tf=TriplesFactory(path='data/exportData.csv')
    training,testing=tf.split()
    pipeline_result=pipeline(
        training_triples_factory=training,
        testing_triples_factory=testing,
        device='gpu',
        model='TransE',
        training_kwargs=dict(num_epochs = 1000)
    )
    losses = pipeline_result.get_losses()

    plt.plot(range(len(losses)), losses)
    plt.xlabel("训练轮数/epoch")
    plt.ylabel("损失函数")
    plt.show()


#    adjusted mean rank is between [0, 1]. Closer to 1 is better!
#    mean rank is a positive integer, with a bound based on the number of entities. Closer to 0 is better!
#    hits@k is reported between [0, 1] and interpreted as a percentage. Closer to 1 is better!


    print(pipeline_result.metric_results.to_df())


    pipeline_result.save_to_directory('test_unstratified_transe')

    #tf.entity_word_cloud()
    #tf.relation_word_cloud()

def pca(embeddings,dim):
    covM = cov(embeddings, rowvar=0)
    s, V = linalg.eig(covM)
    paixu = argsort(s)
    paixuk = paixu[:-(dim+1):-1]
    kwei = V[:,paixuk]
    outputM = embeddings* kwei
    chonggou = (outputM * kwei.T)
    return outputM,chonggou

def plotV(a,labels):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    print("aaa")
    print(a.shape)
    font = { 'fontname':'Microsoft YaHei', 'fontsize':2, 'verticalalignment': 'top', 'horizontalalignment':'center' }

    #ax.scatter(a[:,0], a[:,1])
    ax.set_xlim(-0.5,0.5)
    ax.set_ylim(-0.5,0.5)
    i = 0
    for label, x, y in zip(labels, a[:, 0], a[:, 1]):
        i += 1
        ax.annotate(label, xy = (x, y), xytext = None, ha = 'right', va = 'bottom', **font)
    
    plt.ticklabel_format(style='plain')

    # ax = matplotlib.gca()
    ax = fig.add_subplot(111)
    ax.get_yaxis().get_major_formatter().set_scientific(False)

    plt.title('TransE PCA降维', FontProperties = fontx, fontsize = 30)
    plt.xlabel('X', FontProperties = fontx)
    plt.ylabel('Y', FontProperties = fontx)

    plt.show()
    #matplotlib.use('Agg')
    #plt.savefig('plot_with_labels.svg', dpi = 1500, bbox_inches = 'tight' ,orientation = 'landscape', papertype = 'a4', format = 'svg')
def test():
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
    import pandas as pd
    import json
    import numpy as np
    import matplotlib.pyplot as plt


    tmp = []
    total = []
    for line in open('embedding.json','r', encoding='utf-8'):
        tmp.append(json.loads(line))
    # tmp[2]['embedding']
    for line in tmp:
        if line["ref"] == "SK-2":
            node1 = line["embedding"]
            node1 = eval(node1)
            total.append(node1)
        if line["ref"] == "搭载":
            rel = line["embedding"]
            rel = eval(rel)
            total.append(rel)
        if line["ref"] == "西科斯基S-64“高空吊车”双发涡轮重型起重直升机":
            node2 = line["embedding"]
            node2 = eval(node2)
            total.append(node2)

    # rel = eval(rel)
    # node2 = eval(node2)
    # total = []
    # total.append(node1)
    # t
    total = np.array(total)
    total.shape
    # node1= np.array(node1)
    # node2 = np.array(node2)
    # rel = np.array(rel)
    # node1
    # node1 = node1.reshape(2,-1)
    # node2 = node2.reshape(2,-1)
    # rel = rel.reshape(2,-1)
    # vector = eval(tmp[2]['embedding'])
    # vector = np.array(vector)
    # vector = vector.reshape(-1,1)
    # # vector = vector[0:49]
    # vector = vector.reshape(2,-1)


    def pca(embeddings,dim):
        covM = cov(embeddings, rowvar=0)
        s, V = linalg.eig(covM)
        paixu = argsort(s)
        paixuk = paixu[:-(dim+1):-1]
        kwei = V[:,paixuk]
        outputM = embeddings* kwei
        chonggou = (outputM * kwei.T)
        return outputM,chonggou


    pca=PCA(n_components=2)
    arr=pca.fit_transform(total)
    #     rel_2=pca.fit_transform(rel)
    #     node2_2=pca.fit_transform(node2)
    arr[0] + arr [1] + arr[2]



    plt.axis([-0.2,1,0,0.6])
    plt.arrow(0, 0, -arr[0][0], -arr[0][1],width=0.007,color = 'b')
    plt.annotate('西科斯基S-64高空吊车双发涡轮重型起重直升机', xy=(0.4, 0.15),xytext=(0.5, 0.1), arrowprops=dict(arrowstyle='->'), FontProperties=fontx)
    plt.arrow(0, 0, arr[1][0], arr[1][1],width=0.007,color = 'b')
    # plt.arrow(arr[1][0], arr[1][1],-arr[2][0],-arr[2][1],width=0.005,color = 'b')
    plt.arrow(arr[1][0],arr[1][1], arr[2][0], arr[2][1],width=0.007,color = 'r')
    plt.annotate('搭载', xy=(0.4, 0.44),xytext=(0.3, 0.2), arrowprops=dict(arrowstyle='->'), FontProperties= fontx)  # 添加注释
    plt.arrow(0, 0, arr[1][0], arr[1][1],width=0.007,color = 'r')
    plt.annotate('SK-2', xy=(-0.025, 0.2),xytext=(-0.2, 0.05), arrowprops=dict(arrowstyle='->'))  # 添加注释
    # plt.xlabel('偶数', FontProperties=fontx)
    plt.show()

def saveJson(entities, embeddings_entity, relas, embeddings_rela):
    with open("embedding.json", 'w', encoding='utf-8') as file:
        for rela, embedding in zip(relas, embeddings_rela):
            line = {}
            line['ref'] = rela
            line['embedding'] = json.dumps(embedding.astype(np.float).tolist())
            jsobj = json.dumps(line, ensure_ascii=False)
            file.write(jsobj)
            file.write('\n')
        for entity, embedding in zip(entities, embeddings_entity):
            line = {}
            line['ref'] = entity
            line['embedding'] = json.dumps(embedding.astype(np.float).tolist())
            jsobj = json.dumps(line, ensure_ascii=False)
            file.write(jsobj)
            file.write('\n')
            


def pred():
    model=torch.load('test_unstratified_transe/trained_model.pkl')

    #get entity embedding vector
    embeddings = model.entity_embeddings.weight.detach().cpu().numpy()
    print(embeddings.shape)
    print(embeddings[0])
    names = sorted(
        model.triples_factory.entity_to_id,
        key=model.triples_factory.entity_to_id.get,
    )
    rela_embeddings = model.relation_embeddings.weight.detach().cpu().numpy()
    logger.info(rela_embeddings)
    relas = sorted(
        model.triples_factory.relation_to_id,
        key=model.triples_factory.relation_to_id.get,
    )

    saveJson(names, embeddings, relas, rela_embeddings)


    pca_ = PCA(n_components=2)
    a=pca_.fit_transform(embeddings)
    print("after pca",a.shape)


    #generate pca img
    plotV(a,names)
    #word_cloud(names)


    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 400) # 设置打印宽度(**重要**)
    predicted_heads_df=model.predict_heads('搭载','SK-2',remove_known=True)
    print(predicted_heads_df.iloc[0:])
    # print(predicted_heads_df.iloc[0,1])
    return predicted_heads_df.iloc[0, 1]

def predRadarCarryRela(platformName):
    model=torch.load('test_unstratified_transe/trained_model.pkl')
    predicted_heads_df=model.predict_heads('搭载', platformName,remove_known=True)
    print(predicted_heads_df.head(5))
    return predicted_heads_df.iloc[0, 1]


def word_cloud(labels):
    labels_dict=dict()
    for label in labels:
        if label=='':
            continue
        if label in labels_dict:
            labels_dict[label]+=1
        labels_dict[label]=1

    font = r'C:\Windows\Fonts\simfang.ttf'
    wordcloud=WordCloud(
        font_path=font,
        background_color="white",width=1920,height=1080
    ).generate_from_frequencies(labels_dict)

    plt.imshow(wordcloud,interpolation='bilinear')
    plt.axis('off')
    plt.show()

def data_split():
    data=pd.read_csv('simp.csv',header=None,sep=':')
    print(data.shape)
    data=shuffle(data)

    col1=data.iloc[:,[0]]
    col3=data.iloc[:,[2]]

    col2=data.iloc[:,[1]]
    relations=col2.drop_duplicates().values.tolist()

    entity1=col1.drop_duplicates().values.tolist()
    entity3=col3.drop_duplicates().values.tolist()
    entity_=entity1+entity3
    entity=[]
    for val in entity_:
        if val not in entity:
            entity.append(val[0])

    print(len(entity))
    print(len(relations))

    for index,_entity in enumerate(entity):
        print(index,_entity,type(_entity))





    temp_data=data[int(data.shape[0]*0.2):]
    test_data=data[:int(data.shape[0]*0.2)]

    train_data=temp_data[int(temp_data.shape[0]*0.1):]
    valid_data=temp_data[:int(temp_data.shape[0]*0.1)]

    print(valid_data.shape)
    print(train_data.shape)
    print(test_data.shape)

def insert2database():
    path='simp.csv'
    data=pd.read_csv(path,header=None,sep=':')
    print(data)

    graph=Graph("http://localhost:7474",username='neo4j',password='hello')

    matcher=NodeMatcher(graph)

    #start_node=mathcher()

    print(data.shape)

    for i in range(data.shape[0]):
        S=(data.iloc[i,0])
        P=(data.iloc[i,1])
        O=(data.iloc[i,2])

        exit(0)






if __name__ == "__main__":
    # train()
    pred()
    # test()
    #data_split()
    #insert2database()
