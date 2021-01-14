<template>
<div class="extendedWords">
    <i-modal v-model="exportWindowShow" title="导出数据" width="40" :closable="false" :mask-closable="false" :scrollable="true">
        <h3>1. 请选择要导出的数据范围: </h3>
        <i-radioGroup v-model="selected3">
            <i-radio label="当前选中" border :disabled="selectedFlag.length === 0"></i-radio>
            <i-radio label="当前页" border></i-radio>
            <i-radio label="当前项目" border></i-radio>
        </i-radioGroup>
        <h3>2. 请选择要导出的数据格式: </h3>
        <i-radioGroup v-model="selected2">
            <i-radio label="xlsx" border></i-radio>
            <!-- <i-radio label="json" border></i-radio> -->
        </i-radioGroup>

        <div slot="footer">
            <i-button type="default" size="large" @click="modalCancel()">取消</i-button>
            <i-button type="primary" size="large" @click="modalOk()">导出</i-button>
        </div>

    </i-modal>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'exportData',
    data() {
        return {
            selected3: '当前选中',
            selected2: 'xlsx',
        }
    },
    mounted() {
        // console.log(this.detailIndex,this.pageData)
    },
    created() {
        this.selected3 = this.selected1
        //console.log(this.selectedFlag, this.pageData2Export)
    },
    props: ['exportWindowShow', 'selected1', 'selectedFlag', 'pageData2Export', 'pageSize'],
    computed: {
        ...mapState(['baseurl', 'currentComponent']),
    },
    beforeDestroy() {},
    methods: {
        generateData: function (pageData2Export) {
            let toPrint = []
            for (let ele in pageData2Export) {
                let lineData = pageData2Export[ele]
                let temp = []
                temp.push(parseInt(ele) + 1)
                temp.push(lineData.word)
                temp.push(lineData.category.join(','))
                temp.push(lineData.modifiedTime)
                temp.push(lineData.operator)
                temp.push(lineData.length)
                toPrint.push(temp)
            }
            return toPrint
        },
        modalOk() {
            let self = this
            let toPrint = []
            // 设置 header
            toPrint.push(['id', '用户词', '分类', '时间', '操作人', '长度'])
            toPrint.push(['', '', '', '', '', ''])

            if (self.selected3 === '当前选中' || self.selected3 === '当前页') {
                // 筛选当前选中的数据出来
                let pageData2Export = []
                if (self.selectedFlag.length > 0) {
                    for (let ele in self.selectedFlag) {
                        pageData2Export.push(self.pageData2Export[self.selectedFlag[ele] - 1])
                    }

                } else {
                    // 全部打印
                    pageData2Export = self.pageData2Export
                }
                //console.log(pageData2Export)
                toPrint = toPrint.concat(self.generateData(pageData2Export))

                // 统一打印
                //console.log('toPrint', toPrint)
                let worksheet = self.$XLSX.utils.aoa_to_sheet(toPrint)
                let new_workbook = self.$XLSX.utils.book_new()
                self.$XLSX.utils.book_append_sheet(new_workbook, worksheet, "用户词数据")
                self.$XLSX.writeFile(new_workbook, self.currentComponent + '.xlsx')
                self.$emit('update:exportWindowShow', false)

            }

            if (self.selected3 !== '当前选中' && self.selected3 !== '当前页') {
                // 该项目全部数据.先获取项目全部数据
                let Params = {
                    'currentPage': 0,
                    'pageSize': 0
                }
                self.axios({
                        method: 'get',
                        url: self.baseurl + "UserDict/" + self.currentComponent,
                        params: Params
                    })
                    .then(res => {
                        //console.log(res)
                        // self.currentPage = 1
                        let data2 = res.data.content
                        toPrint = toPrint.concat(self.generateData(data2))
                        // 统一打印
                        // console.log('toPrint',toPrint)
                        let worksheet = self.$XLSX.utils.aoa_to_sheet(toPrint)
                        let new_workbook = self.$XLSX.utils.book_new()
                        self.$XLSX.utils.book_append_sheet(new_workbook, worksheet, "用户词典数据")
                        self.$XLSX.writeFile(new_workbook, self.currentComponent + '.xlsx')
                        self.$emit('update:exportWindowShow', false)
                    })
                    .catch(err => {
                        console.log(err)
                        // self.$Message.error(err.response.data.detail);
                    })
            }
        },
        modalCancel() {
            //this.changeDetailWindowShow(false)
            this.$emit('update:exportWindowShow', false)
        }
    }
}
</script>

<style scoped>
h3 {
    margin: 10px auto
}
</style>
