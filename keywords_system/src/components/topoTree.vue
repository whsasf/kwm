<template>
<div class="topoTree">
    <i-modal v-model="topoTreeShow" class-name="hahah" width="900" :styles="{top: '20px'}" :title="'拓词树: ' + '[' + topoTreeKeyWord['kword'] + ']'" :closable="false" :mask-closable="false" :scrollable="true">
        <div class="echart-parent">
            <div class="tree" ref="tree"></div>
        </div>
        <div slot="footer">
            <i-button type="default" size="large" @click="modalCancel()">关闭</i-button>
        </div>
    </i-modal>
</div>
</template>

<script>
//let echarts = require('echarts/lib/echarts')
//import echarts from 'echarts'
// require('echarts/lib/chart/tree')

import {
    mapState
} from 'vuex'

export default {
    name: 'topoTree',

    data() {

        return {

            myEcharts: '',
            //: {},
            xkey: 1,
            xdata: {}
        }
    },
    props: ['topoTreeShow', 'topoTreeKeyWord', 'treeType'],
    components: {},
    computed: {
        ...mapState(['baseurl', 'currentComponent']),
        option: function () {

            let option = {
                tooltip: {
                    trigger: 'item',
                    triggerOn: 'mousemove'
                },
                series: [{
                    type: 'tree',
                    id: 0,
                    name: 'tree1',
                    data: [this.xdata],
                    top: '20px',
                    left: 'center',
                    // symbol: 'circle',
                    symbolSize: 15,
                    roam: true,
                    edgeShape: 'polyline',
                    edgeForkPosition: '60%',
                    initialTreeDepth: 5,

                    itemStyle: {
                        //color: '#fff',
                        borderColor: '#c23531'
                    },
                    lineStyle: {
                        width: 1,
                        color: 'red'
                    },
                    emphasis: {

                    },

                    label: {
                        backgroundColor: '#fff',
                        position: 'left',
                        verticalAlign: 'middle',
                        align: 'right',
                        fontWeight: 'bold',
                        fontSize: '18',
                        color: "#fff",
                        lineHeight: '25',
                        height: '20'
                    },

                    leaves: {
                        label: {
                            position: 'right',
                            verticalAlign: 'middle',
                            align: 'left'
                        }
                    },

                    expandAndCollapse: true,
                    animationDuration: 550,
                    animationDurationUpdate: 750
                }]
            }
            return option

        }

    },
    mounted() {
        // this.echartsInit()
        if (this.topoTreeShow && this.treeType && this.topoTreeKeyWord) {
            this.fetchTopoTree(this.treeType, this.topoTreeKeyWord)
        }
    },
    methods: {
        echartsInit: function () {
            let self = this
            var dom = ''
            if (!self.$refs.tree) {
                return
            } else {
                dom = self.$refs.tree
            }

            self.myEcharts = self.$echarts.init(dom)
            self.myEcharts.showLoading()
        },
        renderEcharts: function (option) {
            if (option && typeof option === "object") {
                // console.log('rendering ...')
                this.myEcharts.hideLoading()
                this.myEcharts.setOption(option, true)
                //this.myEcharts.on('click', function (params) {
                //    console.log(params)
                //})
            }
        },
        fetchTopoTree: function (xtreeType, kwd) {
            // xtreeType：  basic or extended 
            // kwd: the word that trace begins  kwd= {'kword': '', 'status': ''}
            let self = this
            if (xtreeType === 'basic') {
                // 基础词 分析 拓词树
                // console.log('basic', kwd)
                let Params = {
                    'word': kwd['kword'],
                    'status': kwd['status'],
                    'type': 'basic'
                }
                self.axios({
                        method: 'get',
                        url: self.baseurl + 'extendedWords/topoTree/' + self.currentComponent,
                        params: Params
                    })
                    .then(res => {
                        self.xdata = res.data
                        self.echartsInit()
                        self.renderEcharts(self.option)
                    })
                    .catch(err => {
                        console.log(err)
                    })

            } else if (this.treeType === 'extended') {
                // 拓展词，分析 拓词树
                //console.log('extended')

                // 拓展词 分析 拓词树
                // console.log('extended', kwd)
                let Params = {
                    'word': kwd['kword'],
                    'status': kwd['status'],
                    'type': 'extended'
                }
                self.axios({
                        method: 'get',
                        url: self.baseurl + 'extendedWords/topoTree/' + self.currentComponent,
                        params: Params
                    })
                    .then(res => {
                        self.xdata = res.data
                        self.echartsInit()
                        self.renderEcharts(self.option)
                    })
                    .catch(err => {
                        console.log(err)
                    })

            }
        },
        modalCancel: function () {
            this.$emit('update:topoTreeShow', false)
        }
    }
}
</script>

<style scoped>
.echart-parent {
    width: 880px;
    height: 500px;
    overflow: auto;
    border: 1px solid red;
}

.tree {
    height: 500px;
    max-height: 1000px;
}
</style>
