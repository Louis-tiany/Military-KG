<template>
  <div class="gContainer">
    <gSearch @getData="update" />
    <!-- <threeGraph /> -->
    <threeGraph
      :data="data"
      :names="names"
      :labels="labels"
      :linkTypes="linkTypes"
    />
  </div>
</template>

<script>
// @ is an alias to /src
import gSearch from '@/components/gSearch.vue'
import threeGraph from '@/components/threeGraph.vue'

export default {
  name: 'threeView',
  components: {
    gSearch,
    threeGraph
  },
  data () {
    return {
      // d3jsonParser()处理 json 后返回的结果
      data: {
        nodes: [],
        links: []
      },
      names: ['企业', '贸易类型', '地区', '国家'],
      labels: ['Enterprise', 'Type', 'Region', 'Country'],
      linkTypes: ['', 'type', 'locate', 'export']
    }
  },
  methods: {
    // 视图更新
    update (json) {
      console.log('update')
      console.log(json)
      this.d3jsonParser(json)
    },
    /*eslint-disable*/
    // 解析json数据，主要负责数据的去重、标准化
    d3jsonParser (json) {
      const nodes =[]
      const links = [] // 存放节点和关系
      const nodeSet = [] // 存放去重后nodes的id

      for(let node of json['nodes']) {
        if(nodeSet.indexOf(node["id"]) == -1) {
          nodeSet.push(node["id"])
          nodes.push({
            id: node["id"],
            label: node["label"],
            properties: node["properties"]
          })
        }
      }
      
      for(let link of json['links']) {
        if (nodeSet.indexOf(link["source"]) == -1) {
          continue
        }
        if (nodeSet.indexOf(link["target"]) == -1) {
          continue
        }
        links.push({
          source: link["source"],
          target: link["target"],
          type: link["type"],
          properties: link["properties"]
        });
      }


      console.log(nodes)
      console.log(links)
      // this.links = links
      // this.nodes = nodes
      this.data = { nodes, links }
      // return { nodes, links }
    }
  }
}
</script>

<style lang="scss" scoped>
.gContainer {
  position: relative;
  border: 2px #000 solid;
  background-color: #9dadc1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}
</style>
