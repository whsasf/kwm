<template>
<i-drawer class="dataHouse" :title="'数据中转站: 共选中 ' + xdata2.length + ' 个'" v-model="drawerShow.show" :mask="false" width="400" :mask-closable="false" :scrollable="true" :draggable="true" :before-close="onClose">
    <li class="p title">
        <div class="p1">序号</div>
        <div class="p2">url</div>
        <div class="p3">状态</div>
        <div class="p4">操作</div>
    </li>
    <div class="dataHouse-content">
        <li class="p" v-for="(item,index) in xdata2" :key="index">
            <div class="p1">{{parseInt(index)+1}}</div>
            <div class="p2">{{item.url}}</div>
            <div class="p3">{{item.status}}</div>
            <div class="p4">
                <i-button class="dataHouse-delete" type="warning" size="small" @click="remove(index,item.url)">删除</i-button>
            </div>
        </li>
    </div>

    <div class="demo-drawer-footer">
        <i-button style="margin-right: 8px" @click="onCancle">取消</i-button>
        <i-button type="error" style="margin-right: 8px" @click="resetBoth">清空</i-button>

    </div>
</i-drawer>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'dataHouse',
    data() {
        return {
            dataHouse: '',
            dataHouseIndex: '',
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
        //console.log('data updated')
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
        resetBoth: function () {
            this.$emit('reset')
            this.resetLocal()
        },
        resetLocal: function () {
            this.dataHouse = ''
            this.dataHouseIndex = ''

        },
        submitdataHouse: function () {
            this.$emit('update:drawerShow', {
                'show': false
            })
            //this.$emit('reset')
            //this.resetLocal()
        },
        onCancle: function () {
            this.$emit('update:drawerShow', {
                'show': false
            })
            //this.$emit('reset')
            //this.resetLocal()
        },
        remove: function (index, url) {
            this.xdata2.splice(index, 1)
            this.$emit('update:xdata', this.xdata2.reverse())
            this.$emit('updateSelectedOldUrlsList', url)
            // console.log(this.xdata2)
        },
        onClose: function () {
            //this.resetLocal()
            this.$emit('update:drawerShow', {
                'show': false
            })
            //this.$emit('reset')
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

.dataHouse .p {
    display: flex;
    justify-content: center;
    align-items: center;
    border-top: 1px solid green;
}

.dataHouse .p .p1 {
    flex: 1;
    text-align: left;
    border-left: 1px solid green;
    border-right: 1px solid green;
    padding: 2px 1px
}

.dataHouse .p .p2 {
    flex: 5;
    text-align: left;
    border-right: 1px solid green;
    padding: 2px 1px;
    overflow: auto
}

.dataHouse .p .p3 {
    flex: 2;
    text-align: left;
    padding: 2px 1px;
    border-right: 1px solid green;
}

.dataHouse .p .p4 {
    flex: 2;
    text-align: center;
    padding: 2px 1px;
    border-right: 1px solid green;
}

.dataHouse-delete {
    margin-left: 5px;
    margin-right: 3px
}

.dataHouse .title {
    border-bottom: 1px solid green;
}

>>>.ivu-drawer-header {
    padding: 5px 16px
}

.dataHouse-content {
    max-height: 450px;

    overflow: auto;
    border: 1px solid green
}
</style>
