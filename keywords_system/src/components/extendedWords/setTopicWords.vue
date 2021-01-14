<template>
<i-drawer class="topicWord" :title="'主题词设置: 候选共 ' + xdata2.length + ' 个'" v-model="drawerShow.show" :mask="false" width="330" :mask-closable="false" :scrollable="true" :draggable="true" :before-close="onClose">
    <li class="p title">
        <div class="p1">序号</div>
        <div class="p2">拓展词</div>
        <div class="p3">操作</div>
    </li>
    <div class="topicWord-content">
        <li class="p" v-for="(item,index) in xdata2" :key="index">
            <div class="p1">{{parseInt(index)+1}}</div>
            <div v-if="topicWord === item.word" class="p2 word" style="font-weight: bold; background-color: yellow">{{item.word}}</div>
            <div v-else class="p2 word">{{item.word}}</div>
            <div class="p3">
                <i-button v-if="topicWord === item.word" class="topicWord-set" type="success" size="small" @click="reSetTopic()">重选主题词</i-button>
                <i-button :disabled="topicWord !== '' && topicWord !== item.word" v-else class="topicWord-set" type="success" size="small" @click="set2Topic(item.word,index)">设为主题词</i-button>
                <i-button :disabled="topicWord === item.word" class="topicWord-delete" type="warning" size="small" @click="remove(index)">删除</i-button>
            </div>
        </li>
    </div>

    <div class="topicWord-statics">
        <div class="topicWord-statics-normal">
            <div class="topicWord-statics-hang"><span>总PV:</span> <span class="topicWord-statics-normal-number">{{PVSum}}</span></div>
            <div class="topicWord-statics-hang"><span>平均竞价:</span> <span class="topicWord-statics-normal-number">{{bidPriceAvg}}</span></div>
            <div class="topicWord-statics-hang"><span>平均竞争力:</span> <span class="topicWord-statics-normal-number">{{indexAvg}}</span></div>
        </div>
        <div class="topicWord-statics-mobile">
            <div class="topicWord-statics-hang"><span>总PV-移动:</span> <span class="topicWord-statics-normal-number">{{PVSumM}}</span></div>
            <div class="topicWord-statics-hang"><span>平均竞价-移动:</span> <span class="topicWord-statics-normal-number">{{bidPriceAvgM}}</span></div>
            <div class="topicWord-statics-hang"><span>平均竞争力-移动:</span> <span class="topicWord-statics-normal-number">{{indexAvgM}}</span></div>
        </div>
    </div>
    <div class="demo-drawer-footer">
        <i-button style="margin-right: 8px" @click="onCancle">取消</i-button>
        <i-button type="primary" @click="submitTopicWord">提交</i-button>
    </div>
</i-drawer>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'setTopicWord',
    data() {
        return {
            topicWord: '',
            topicWordIndex: '',
            PVSum: 0,
            bidPriceAvg: 0,
            indexAvg: 0,
            PVSumM: 0,
            bidPriceAvgM: 0,
            indexAvgM: 0,
            styles: {
                height: '300px',
                overflow: 'auto',
                //paddingBottom: '53px',
            }
        }
    },
    updated() {
        // console.log(this.detailIndex,this.pageData)
        // 计算 PV ，等
        //console.log('updated')
        //console.log(this.xdata)
        //if (this.xdata.length !== 0) {

        let out = this.jisusn(this.xdata2)

        this.PVSum = out['PVSum']
        this.bidPriceAvg = out['bidPriceAvg']
        this.indexAvg = out['indexAvg']
        this.PVSumM = out['PVSumM']
        this.bidPriceAvgM = out['bidPriceAvgM']
        this.indexAvgM = out['indexAvgM']
        //}
    },
    created() {

    },
    props: ['drawerShow', 'xdata'],
    computed: {
        ...mapState(['baseurl', 'currentComponent']),
        xdata2: {
            get: function () {
                return JSON.parse(JSON.stringify(this.xdata)).reverse()
            },
            set: function () {
                return this.xdata2
            }
        }
    },
    beforeDestroy() {},
    methods: {
        resetLocal: function () {
            this.topicWord = ''
            this.topicWordIndex = ''
            this.topicWord = ''
            this.topicWordIndex = ''
            this.PVSum = 0
            this.bidPriceAvg = 0
            this.indexAvg = 0
            this.PVSumM = 0
            this.bidPriceAvgM = 0
            this.indexAvgM = 0

        },
        submitTopicWord: function () {
            if (this.topicWord === '') {
                this.$Message.warning('还未选择主题词!');
                return
            }
            let uids = []
            for (let ele in this.xdata2) {
                let lineData = this.xdata2[ele]
                uids.push({
                    'uid': lineData['id'],
                    'word': lineData['word']
                })
            }
            //console.log('uids', uids)
            this.$emit('submitTopicWord', {
                'topicWord': this.topicWord,
                'uids': uids
            })
            this.$emit('update:drawerShow', {
                'show': false
            })
            this.$emit('reset')
            this.resetLocal()
        },
        onCancle: function () {
            this.$emit('update:drawerShow', {
                'show': false
            })
            this.$emit('reset')
            this.resetLocal()
        },
        reSetTopic: function () {
            this.topicWord = ''
            this.topicWordIndex = ''
        },
        set2Topic: function (item, index) {
            this.topicWord = item
            this.topicWordIndex = index
            // console.log(this.topicWord, index)
        },
        remove: function (index) {
            this.xdata2.splice(index, 1)
            this.$emit('update:xdata', this.xdata2.reverse())
            // console.log(this.xdata2)
        },
        onClose: function () {
            this.resetLocal()
            this.$emit('update:drawerShow', {
                'show': false
            })
            this.$emit('reset')
        },
        jisusn: function (mydata) {
            let PVSum = 0
            let bidPriceSum = 0
            let indexSum = 0
            let PVSumM = 0
            let bidPriceSumM = 0
            let indexSumM = 0
            for (let ele in mydata) {
                let lineData = mydata[ele]
                PVSum = PVSum + lineData['searchCount']
                indexSum = indexSum + lineData['baiduIndex']
                bidPriceSum = bidPriceSum + lineData['bidPrice']

                PVSumM = PVSumM + lineData['searchCountM']
                indexSumM = indexSumM + lineData['baiduIndexM']
                bidPriceSumM = bidPriceSumM + lineData['bidPriceM']

            }
            // 计算最终结果 并返回
            let length = mydata.length
            if (length === 0) {
                length = 1
            }
            let out = {
                'PVSum': PVSum,
                'bidPriceAvg': Math.floor(bidPriceSum / length * 100) / 100,
                'indexAvg': Math.floor(indexSum / length * 100) / 100,
                'PVSumM': PVSumM,
                'bidPriceAvgM': Math.floor(bidPriceSumM / length * 100) / 100,
                'indexAvgM': Math.floor(indexSumM / length * 100) / 100
            }
            //console.log('out', out)
            return (out)

        }

    }
}
</script>

<style scoped>
.demo-drawer-footer {
    width: 100%;
    position: absolute;
    bottom: 0;
    left: 0;
    height: 38px;
    border-top: 1px solid #e8e8e8;
    padding: 5px 16px;
    text-align: right;
    background: #fff;
}

>>>.ivu-drawer.ivu-drawer-right {
    height: 600px !important;
    top: 150px !important;
    border: 1px solid green !important;
}

.topicWord .p {
    display: flex;
    justify-content: center;
    align-items: center;
    border-top: 1px solid green;
}

.topicWord .p .p1 {
    flex: 1;
    text-align: left;
    border-left: 1px solid green;
    border-right: 1px solid green;
    padding: 2px 1px
}

.topicWord .p .p2 {
    flex: 3;
    text-align: left;
    border-right: 1px solid green;
    padding: 2px 1px
}

.topicWord .p .p3 {
    flex: 5;
    text-align: center;
    padding: 2px 1px;
    border-right: 1px solid green;
}

.topicWord-delete {
    margin-left: 5px;
    margin-right: 3px
}

.topicWord .title {
    border-bottom: 1px solid green;
}

>>>.ivu-drawer-header {
    padding: 5px 16px
}

.topicWord-content {
    max-height: 380px;
    height: 380px;
    overflow: auto;
    border: 1px solid green
}

.topicWord-statics {
    margin-top: 10px;
    display: flex;
    justify-content: space-between
}

.topicWord-statics-normal-number {
    font-weight: bold
}

.topicWord-statics-hang {
    display: flex;
    justify-content: space-between
}
</style>
