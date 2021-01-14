<template>
<div>
    <i-modal v-model="similarShow" :title=" basicWord + ' 的临近词'" width="80%" :closable="true" :mask-closable="false" :scrollable="true">
    <div class="basicWords-button-group2">
        <i-button type="error" icon="md-trash" @click="deleteConfirm">删除</i-button>
        <i-draggable class="dragable-warp" v-model="sortItems" @start="drag=true" @end="drag=false" @change="onChange">
            <div class="dragablex" v-for="(item,index) in sortItems" :key="index">
                <div class="label">{{item.name}}</div>
                <i-select v-model="item.model" style="width:65px" @on-change="onChange">
                    <i-option v-for="item2 in sortList" :value="item2.value" :key="item2.value">{{ item2.label }}</i-option>
                </i-select>
            </div>
        </i-draggable>
        <i-button style="color: #fff;background-color: #54616f" @click="setStopWord">设为停止词</i-button>
        <i-button style="color: #fff;background-color: #7b5ae4" @click="setInvalidWord">设为无效词</i-button>
    </div>
    <i-page :total="itemCount" :current="currentPage" placement="bottom" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />
    <i-table class="basicWords-table" :columns="columns1" :data="basicWordsItemData" :loading="tableLoading" @on-selection-change="handleSelectRow()" ref="table" stripe border @on-filter-change="handleFilter" @on-sort-change="handleSort"></i-table>
    <i-page :total="itemCount" :current="currentPage" placement="top" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />

    <!--弹出框都在此地-->
    <i-checkSource :key="checkSourceKey" :dataRequired="dataRequired" :checkSourceShow.sync="checkSourceShow"></i-checkSource>
    <i-exportData :key="expordDataKey" :pageSize="pageSize" :selectedFlag="selectedFlag" :selected1="selected1" :pageData2Export="pageData2Export" :exportWindowShow.sync="exportWindowShow"></i-exportData>
 </i-modal>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
import checkSource from '@/components/basicWords/checkSource.vue'
import exportData from '@/components/basicWords/exportData.vue'

export default {
    name: 'similarWords',
    data() {
        return {
            similarShow: JSON.parse(JSON.stringify(this.similarShow2)),
            expandStatus: '',
            dbName: '', // 当前项目 所在的  mongo 数据库 名称
            sortList: [{
                    'value': 'default',
                    'label': '默认'
                },
                {
                    'value': 'asc',
                    'label': '升序'
                },
                {
                    'value': 'desc',
                    'label': '降序'
                }
            ],
            sortItems: [{
                    "name": "长度",
                    "id": 'Length',
                    'model': 'default'
                },
                {
                    "name": "权重",
                    "id": 'weight',
                    'model': 'default',
                }
            ],
            selected1: '当前选中',
            selectedFlag: [],
            expordDataKey: -20,
            pageData2Export: [],
            exportWindowShow: false,
            // topoTreeData: {},
            dataRequired: '',
            checkSourceKey: 0,
            checkSourceShow: false,
            searchItem: '',
            searchResult: [],
            dateRange: ['', ''],
            categoryChecked: [],
            statusChecked: [],
            weightChecked: [],
            lengthChecked: [],
            sortDict: {},
            selectedItemList: [],
            itemCount: 0,
            currentPage: 1,
            pageSize: 10,
            basicWordsItemData: [],
            tableLoading: false,
            columns1: [{
                    type: 'selection',
                    width: 30,
                    align: 'center',
                    resizable: true,
                    fixed: 'left'
                },
                {
                    title: 'id',
                    key: 'id',
                    width: 45,
                    align: 'center',
                    //sortable: true,
                    resizable: true,
                    fixed: 'left'
                },
                {
                    title: '临近词',
                    key: 'word',
                    align: 'center',
                    fixed: 'left',
                    minWidth: 120,
                    resizable: true

                },
                {
                    title: '分类',
                    key: 'category',
                    align: 'center',
                    minWidth: 100,
                    resizable: true,
                    filters: [],
                    filterMultiple: true,
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        //if (row.category.includes(value)){
                        return row //什么都不做，由专门的函数进行后端筛选
                        //}
                    },
                    render: (h, params) => {
                        if (params.row.category) {
                            return (h('p', params.row.category.join(';')))
                        } else {
                            return (h('p', ''))
                        }

                    }
                },
                {
                    title: '状态',
                    key: 'status',
                    align: 'center',
                    width: 120,
                    resizable: true,
                    filters: [{
                        'label': '停止',
                        'value': '停止'
                    }, {
                        'label': '无效',
                        'value': '无效'
                    }, {
                        'label': '已添加',
                        'value': '已添加'
                    }, {
                        'label': '拓词中',
                        'value': '拓词中'
                    }, {
                        'label': '已拓词',
                        'value': '已拓词'
                    }, ],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        //if (row.status === value){
                        return row //什么都不做，由专门的函数进行后端筛选
                        //}
                    },
                    render: (h, params) => {
                        // console.log(params)
                        if (params.row.status === '无效') {
                            return h('p', {
                                style: {
                                    'background-color': 'rgba(123, 90, 228, 0.3)',
                                }
                            }, params.row.status + ' (' + params.row.timestamp + ') ')
                        } else if (params.row.status === '停止') {
                            return h('p', {
                                style: {
                                    'background-color': 'rgba(84, 97, 111, 0.3)',
                                }
                            }, params.row.status + ' (' + params.row.timestamp + ') ')
                        } else if (params.row.status === '已添加') {
                            return h('p', params.row.status + ' (' + params.row.timestamp + ') ')
                        } else if (params.row.status === '拓词中') {
                            return h('p', {
                                style: {
                                    'background-color': 'rgba(151, 221, 144, 0.5)',
                                }
                            }, params.row.status + ' (' + params.row.timestamp + ') ')
                        } else if (params.row.status === '已拓词') {
                            return h('p', {
                                style: {
                                    'background-color': 'rgba(7, 249, 23, 0.5)',
                                }
                            }, params.row.status + ' (' + params.row.timestamp + ') ')
                        }

                    }
                },
                {
                    title: '生成时间',
                    key: 'timestamp',
                    align: 'center',
                    width: 90,
                    resizable: true
                },
                {
                    title: '出处',
                    key: 'source',
                    align: 'center',
                    minWidth: 120,
                    resizable: true,
                    render: (h, params) => {
                        if (params.row) {
                            return h('a', {
                                style: {
                                    color: '#057009',
                                    'font-weight': '800'
                                },
                                on: {
                                    click: () => {
                                        // window.open(params.row.url)
                                        // 激活 seeUrlConfig
                                        // console.log(params.row.root)
                                        this.handleSource(params.row.word, params.row.source)
                                        // this.seeUrlConfigKey = this.seeUrlConfigKey +1
                                        // this.showSeeUrlConfig = true
                                    }
                                }
                            }, params.row.source[0])
                        }
                    }
                },
                {
                    title: '长度',
                    key: 'Length',
                    align: 'center',
                    width: 80,
                    // sortable: 'custom',
                    resizable: true,
                    // filters 对应项目:
                    // 1 -> [0,3], 2 -> [3,5], 3 -> [5,8], 4 -> [8,13],5 -> [13,18], 6 -> [18,25]
                    filters: [{
                        'label': '0-3',
                        'value': '1'
                    }, {
                        'label': '3-5',
                        'value': '2'
                    }, {
                        'label': '5-8',
                        'value': '3'
                    }, {
                        'label': '8-13',
                        'value': '4'
                    }, {
                        'label': '13-18',
                        'value': '5'
                    }, {
                        'label': '18-25',
                        'value': '6'
                    }],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        return row //什么都不做，由专门的函数进行后端筛选
                    },
                    render: (h, params) => {
                        // console.log(params.row)
                        return (h('p', params.row.Length)) //.length))
                    }
                },
                {
                    title: '权重',
                    key: 'weight',
                    align: 'center',
                    // sortable: 'custom',
                    width: 80,
                    // 1 -> [0,0.3], 2 -> [0.3,0.5], 3 -> [0.5,1], 4 -> [1,5],5 -> [5,10], 6 -> [10,20], 7 -> [20,50]
                    filters: [{
                        'label': '0-0.3',
                        'value': '1'
                    }, {
                        'label': '0.3-0.5',
                        'value': '2'
                    }, {
                        'label': '0.5-1',
                        'value': '3'
                    }, {
                        'label': '1-5',
                        'value': '4'
                    }, {
                        'label': '5-10',
                        'value': '5'
                    }, {
                        'label': '10-20',
                        'value': '6'
                    }, {
                        'label': '20-50',
                        'value': '7'
                    }],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        return row //什么都不做，由专门的函数进行后端筛选
                    },
                    resizable: true,
                }
            ],
        }
    },
    props: ['basicWord','categories','similarShow2'],
    computed: {
        ...mapState(['baseurl', 'currentComponent','expandAddr']),
    },
    components: {
        'i-checkSource': checkSource,
        'i-exportData': exportData,
    },
    mounted() {
        // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize}
        // this.loading = true
        let self = this
        self.batchSearch(self.basicWord)
        self.columns1[3].filters = self.categories
    },
    methods: {
        onChange: function () {
            //console.log('sort changed')
            let self = this
            // 得到 需要的格式
            let sortDict = {}
            for (let ele in self.sortItems) {
                let lineData = self.sortItems[ele]
                if (lineData.model !== 'default') {
                    sortDict[lineData.id] = lineData.model
                }
            }
            //console.log('sortDict', sortDict)
            self.sortDict = sortDict

            //if (Object.keys(sortDict).length !== 0) { // 为空也发送，刷新上一次保留的 排序顺序
            // 发送排序请求
            self.currentPage = 1
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'extendedWordItemId': '',
                'statusFilter': encodeURIComponent(self.statusChecked),
                'dateRange': encodeURIComponent(self.dateRange),
                'wordPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'baiduIndexFilter': encodeURIComponent(self.baiduIndexChecked),
                'lengthFilter': encodeURIComponent(self.lengthChecked),
                'bidPriceFilter': encodeURIComponent(self.bidPriceChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }
            //    console.log(Params)
            self.fetchItemsES(Params)
            //} //else {
            //   self.$Message.info('不排序');
            //}
        },
        exportDataX: function () {
            let self = this
            // 当没有选项被选中时，默认选中打印当前页
            if (self.selectedItemList.length !== 0) {
                if (self.selectedItemList.length === self.basicWordsItemData.length) {
                    // 等同于选择了 当前页
                    self.selected1 = '当前页'
                    let selectedFlag = []
                    // for (let ele=1; ele <=  self.UrlItemData.length; ele++){
                    //   selectedFlag.push(ele)
                    // }
                    self.selectedFlag = selectedFlag

                } else {
                    self.selected1 = '当前选中'
                    let selectedFlag = []
                    for (let ele in self.selectedItemList) {
                        selectedFlag.push(self.selectedItemList[ele].id)
                    }
                    self.selectedFlag = selectedFlag
                }

            } else {
                self.selected1 = '当前页'
                let selectedFlag = []
                //for (let ele=1; ele <=  self.UrlItemData.length; ele+1){
                //   selectedFlag.push(ele)
                //}
                self.selectedFlag = selectedFlag
            }

            // 把当前页数据传进去
            self.pageData2Export = self.basicWordsItemData
            self.expordDataKey++
            self.exportWindowShow = true

        },
        handleSource: function (word, source) {
            // console.log(word,source)
            this.dataRequired = [word, source]
            this.checkSourceKey++
            this.checkSourceShow = true
        },
        handleSort: function (column) {
            let self = this
            // console.log(column.key,column.order)
            let sortDict = self.sortDict
            // 每一次点击，都会  重置 该字典
            if (column.order === 'normal') {
                delete sortDict[column.key]
            } else {
                sortDict[column.key] = column.order
            }

            // 删除 里面的normal 项:
            for (let ele in sortDict) {
                if (sortDict[ele] === 'normal') {
                    delete sortDict.ele
                }
            }
            self.sortDict = Object.assign({}, sortDict)
            //console.log('cccc', self.sortDict)
            if (Object.keys(sortDict).length !== 0) {
                // 发送排序请求
                self.currentPage = 1
                let Params = {
                    'currentPage': self.currentPage,
                    'pageSize': self.pageSize,
                    'extendedWordItemId': '',
                    'statusFilter': encodeURIComponent(self.statusChecked),
                    'dateRange': encodeURIComponent(self.dateRange),
                    'wordPart': self.searchItem.toLowerCase(),
                    'categoryFilter': encodeURIComponent(self.categoryChecked),
                    'baiduIndexFilter': encodeURIComponent(self.baiduIndexChecked),
                    'lengthFilter': encodeURIComponent(self.lengthChecked),
                    'bidPriceFilter': encodeURIComponent(self.bidPriceChecked),
                    'sortDict': JSON.stringify(self.sortDict)
                }
                //    console.log(Params)
                self.fetchItemsES(Params)
            } else {
                self.$Message.info('排序条件不满足!');
            }
        },
        batchSearch: function (part) {
            // 输入特定查询，按下回车键或 搜索按钮时 ，触发，会返回所有符合条件的项目 或为空
            let self = this
            //console.log('batchSearch')
            self.searchItem = part
            this.searchResult = []
            // 下面进行 batchSearch
            self.currentPage = 1
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'dateRange':encodeURIComponent(self.dateRange),'wordPart':self.searchItem.toLowerCase() ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'statusFilter': encodeURIComponent(self.statusChecked)}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'basicWordItemId': '',
                'dateRange': encodeURIComponent(self.dateRange),
                'wordPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'lengthFilter': encodeURIComponent(self.lengthChecked),
                'weightFilter': encodeURIComponent(self.weightChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }
            // console.log(Params)
            self.fetchItemsES(Params)

        },
        changeBasicWordStatus: function (id, status) {
            let self = this
            let myData = {
                'status': status
            }
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            self.axios({
                    method: 'patch',
                    url: self.baseurl + 'basicWords/' + self.currentComponent + '/' + id,
                    data: myData,
                    params: Params

                })
                .then(() => {
                    // console.log(res)
                    // self.currentPage = 1
                    //if (res.data.count !== '') {
                    //    self.itemCount = res.data.count
                    //}
                    //self.basicWordsItemData = res.data.content
                    //self.selectedItemList = []
                    setTimeout( ()=>{
                    self.batchSearch(self.basicWord)},2500)
                    // console.log(self.basicWordsItemData)
                })
                .catch(err => {
                    // console.log(err)
                    self.selectedItemList = []
                    //console.log(err.response.data.detail)
                    self.$Message.error(err.response.data.detail);
                })
        },
        setStopWord: function () {
            let self = this
            // 要想添加到 停止词，需要先检查 该词是否已存在在 无效词和用户词？ 如果已 存在于 两者中任何一个，则弹窗提示，是否 强力插入，如果是，则从 前者中 删除该词，并 插入到无效词。
            // 如果否，则跳过对该词的操作。如此看来， 需要单个词进行 循环操作，比较 麻烦。

            if (self.selectedItemList.length === 0) {
                //console.log('no delete')
                self.$Message.warning('无待设置项!');
            } else {
                for (let element in self.selectedItemList) {
                    // 0- 获取 单个数据 
                    let tempLine = {
                        'id': self.selectedItemList[element]['_id']['$oid'],
                        'status': self.selectedItemList[element].status,
                        'word': self.selectedItemList[element].word,
                        'operator': localStorage.getItem('kwmUser'),
                        'source': '基础词'
                    }
                    //console.log('tempLine', tempLine)

                    // 1- 判断如果已经是 停止词，那么 直接跳过
                    if (tempLine.status === '停止') {
                        // 已经是 停止词了，直接跳过
                        self.$Message.info(tempLine['word'] + '已经是停止词，无需设置,跳过 ...');
                        continue
                    }

                    // 2 - 首先 查看该词是否在无效词
                    let Params = {
                        'keyword': tempLine['word'],
                        'fullMatch': true
                    }
                    self.axios({
                            method: 'get',
                            url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                            params: Params
                        })
                        .then(res => {
                            //console.log(res)
                            if (res.data.count > 0) {
                                // 存在于 无效词典中 
                                //console.log(tempLine['word'] + ' 存在于 无效词中')

                                //
                                //弹窗确认，是否要 强制 插入,并从 无效词中已出！！
                                //弹窗暂时放弃，无论从技术上还是 操作上 都 有些难度
                                //
                                //
                                //self.$Modal.confirm({
                                //    title: '任性添加确认',
                                //    content: '<p>"' + tempLine['word'] + '"已经存在于无效词典中,是否从中删除并添加到停止词典？如果确定继续,请确认</p>',
                                //    onOk: () => {
                                //console.log('确认添加!')

                                // 首先从 无效词典中，删除该词
                                self
                                    .axios({
                                        method: "delete",
                                        url: self.baseurl + "InvalidDict/" + self.currentComponent,
                                        data: [tempLine['word']],
                                    })
                                    .then(() => {
                                        //console.log('从无效词中删除成功,下面添加到 停止词中')

                                        // 然后，将该词添加到 停止词
                                        let xdata = [{
                                            'word': tempLine['word'],
                                            'operator': localStorage.getItem('kwmUser'),
                                            'source': '基础词',
                                            'exStatus': tempLine['status']
                                        }]
                                        self.axios({
                                                method: 'post',
                                                url: self.baseurl + 'StopDict/',
                                                data: xdata
                                            })
                                            .then(() => {
                                                //console.log('添加到 停止词成功!')

                                                // 然后哦，更改 在基础词中的状态
                                                self.changeBasicWordStatus(tempLine['id'], '停止')
                                            })
                                            .catch(err => {
                                                //console.log(err)
                                                self.$Message.error(err.response.data.detail);
                                                self.changeBasicWordStatus(tempLine['id'], '停止')
                                            })

                                    })
                                    .catch((err) => {
                                        console.log(err);
                                        self.$Message.error("删除失败");
                                    });

                                //},
                                //onCancel: () => {
                                //    console.log('取消添加!')
                                //    //this.$Message.info('已取消');
                                //    return
                                //}
                                //});
                            } else {
                                //console.log('不存在于 无效词典中，继续搜索用户词典')

                                // 接着查看是否 存在于 用户词中 
                                let Params = {
                                    'keyword': tempLine['word'],
                                    'fullMatch': true
                                }
                                self.axios({
                                        method: 'get',
                                        url: self.baseurl + 'UserDict/' + self.currentComponent,
                                        params: Params
                                    })
                                    .then(res => {
                                        if (res.data.count > 0) {
                                            // 存在于 用户词典中
                                            // 弹窗提示用户，是否 强力插入
                                            //self.$Modal.confirm({
                                            //    title: '任性添加确认',
                                            //    'z-index': element,

                                            //    content: '<p>"' + tempLine['word'] + '"已经存在于用户词典中,是否从中删除并添加到停止词典？如果确定继续,请确认</p>',
                                            //    onOk: () => {
                                            // 首先从 用户词典中，删除该词
                                            self
                                                .axios({
                                                    method: "delete",
                                                    url: self.baseurl + "UserDict/" + self.currentComponent,
                                                    data: [{
                                                        'word': tempLine['word']
                                                    }],
                                                })
                                                .then(() => {
                                                    //console.log('从用户词中删除成功,下面添加到 停止词中')

                                                    // 然后，将该词添加到 停止词
                                                    let xdata = [{
                                                        'word': tempLine['word'],
                                                        'operator': localStorage.getItem('kwmUser'),
                                                        'source': '基础词',
                                                        'exStatus': tempLine['status']
                                                    }]
                                                    self.axios({
                                                            method: 'post',
                                                            url: self.baseurl + 'StopDict/',
                                                            data: xdata
                                                        })
                                                        .then(() => {
                                                            //console.log('添加到 停止词成功!')

                                                            // 然后哦，更改 在基础词中的状态
                                                            self.changeBasicWordStatus(tempLine['id'], '停止')
                                                        })
                                                        .catch(err => {
                                                            //console.log(err)
                                                            self.$Message.error(err.response.data.detail);
                                                            self.changeBasicWordStatus(tempLine['id'], '停止')
                                                        })

                                                })
                                                .catch((err) => {
                                                    console.log(err);
                                                    self.$Message.error("删除失败");
                                                });
                                            //},
                                            //onCancel: () => {
                                            //    console.log('取消添加!')
                                            //    //this.$Message.info('已取消');
                                            //    return
                                            //}
                                            //});
                                        } else {
                                            // 不存在于用户词典中
                                            // 那么，接下来直接往 停止词典里面插入，不管存不存在，如果存在，会自动报错跳过
                                            // 然后，将该词添加到 停止词
                                            let xdata = [{
                                                'word': tempLine['word'],
                                                'operator': localStorage.getItem('kwmUser'),
                                                'source': '基础词',
                                                'exStatus': tempLine['status']
                                            }]
                                            self.axios({
                                                    method: 'post',
                                                    url: self.baseurl + 'StopDict/',
                                                    data: xdata
                                                })
                                                .then(() => {
                                                    //console.log('添加到 停止词成功!')

                                                    // 然后哦，更改 在基础词中的状态
                                                    self.changeBasicWordStatus(tempLine['id'], '停止')
                                                })
                                                .catch(err => {
                                                    //console.log(err)
                                                    self.$Message.error(err.response.data.detail);
                                                    self.changeBasicWordStatus(tempLine['id'], '停止')
                                                })

                                        }
                                    })
                                    .catch(err => {
                                        console.log(err)
                                    })
                            }
                        })
                        .catch(err => {
                            console.log(err)
                        })

                }
            }
        },
        setInvalidWord: function () {
            let self = this
            // 要想添加到 无效词，需要先检查 该词是否已存在在 停止词和用户词？ 如果已 存在于 两者中任何一个，则弹窗提示，是否 强力插入，如果是，则从 前者中 删除该词，并 插入停止词。
            // 如果否，则跳过对该词的操作。如此看来， 需要单个词进行 循环操作，比较 麻烦。
            if (self.selectedItemList.length === 0) {
                //console.log('no delete')
                self.$Message.warning('无待设置项!');
            } else {
                for (let element in self.selectedItemList) {
                    // 0- 获取 单个数据 
                    let tempLine = {
                        'id': self.selectedItemList[element]['_id']['$oid'],
                        'word': self.selectedItemList[element].word,
                        'status': self.selectedItemList[element].status,
                        'operator': localStorage.getItem('kwmUser'),
                        'source': '基础词'
                    }
                    // console.log('tempLine', tempLine)

                    // 1- 判断如果已经是 无效词，那么 直接跳过
                    if (tempLine.status === '无效') {
                        // 已经是 无效词了，直接跳过
                        self.$Message.info(tempLine['word'] + '已经是无效词，无需设置,跳过 ...');
                        continue
                    }

                    // 2 - 首先 查看该词是否在停止词中
                    let Params = {
                        'keyword': tempLine['word'],
                        'fullMatch': true
                    }
                    self.axios({
                            method: 'get',
                            url: self.baseurl + 'StopDict/',
                            params: Params
                        })
                        .then(res => {
                            //console.log(res)
                            if (res.data.count > 0) {
                                // 存在于 停止词典中 
                                //console.log(tempLine['word'] + ' 存在于 停止词中')

                                // 弹窗确认，是否要 强制 插入,并从 停止词中移除！！
                                //self.$Modal.confirm({
                                //    title: '任性添加确认',
                                //    'z-index': element,

                                //    content: '<p>"' + tempLine['word'] + '"已经存在于停止词典中,是否从中删除并添加到无效词典？如果确定继续,请确认</p>',
                                //    onOk: () => {
                                //console.log('确认添加!')

                                // 首先从 停止词典中，删除该词
                                self
                                    .axios({
                                        method: "delete",
                                        url: self.baseurl + "StopDict/",
                                        data: [tempLine['word']],
                                    })
                                    .then(() => {
                                        //console.log('从停止词中删除成功,下面添加到 无效词中')

                                        // 然后，将该词添加到 无效词典
                                        let xdata = [{
                                            'word': tempLine['word'],
                                            'operator': localStorage.getItem('kwmUser'),
                                            'source': '基础词',
                                            'exStatus': tempLine['status']
                                        }]
                                        self.axios({
                                                method: 'post',
                                                url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                                                data: xdata
                                            })
                                            .then(() => {
                                                //console.log('添加到 无效词成功!')

                                                // 然后哦，更改 在基础词中的状态
                                                self.changeBasicWordStatus(tempLine['id'], '无效')
                                            })
                                            .catch(err => {
                                                //console.log(err)
                                                self.$Message.error(err.response.data.detail);
                                                self.changeBasicWordStatus(tempLine['id'], '无效')
                                            })

                                    })
                                    .catch((err) => {
                                        console.log(err);
                                        self.$Message.error("删除失败");
                                    });

                                //},
                                //onCancel: () => {
                                //    console.log('取消添加!')
                                //    //this.$Message.info('已取消');
                                //    return
                                //}
                                //});
                            } else {
                                //console.log('不存在于 停止词典中，继续搜索用户词典')

                                // 接着查看是否 存在于 用户词中 
                                let Params = {
                                    'keyword': tempLine['word'],
                                    'fullMatch': true
                                }
                                self.axios({
                                        method: 'get',
                                        url: self.baseurl + 'UserDict/' + self.currentComponent,
                                        params: Params
                                    })
                                    .then(res => {
                                        if (res.data.count > 0) {
                                            // 存在于 用户词典中
                                            // 弹窗提示用户，是否 强力插入
                                            //console.log('存在于 用户词典中')
                                            //self.$Modal.confirm({
                                            //    title: '任性添加确认',
                                            //    'z-index': element,

                                            //    content: '<p>"' + tempLine['word'] + '"已经存在于用户词典中,是否从中删除并添加到无效词典？如果确定继续,请确认</p>',
                                            //    onOk: () => {
                                            //        // 首先从 用户词典中，删除该词
                                            self
                                                .axios({
                                                    method: "delete",
                                                    url: self.baseurl + "UserDict/" + self.currentComponent,
                                                    data: [{
                                                        'word': tempLine['word']
                                                    }],
                                                })
                                                .then(() => {
                                                    //console.log('从用户词中删除成功,下面添加到 无效词中')

                                                    // 然后，将该词添加到 无效词
                                                    let xdata = [{
                                                        'word': tempLine['word'],
                                                        'operator': localStorage.getItem('kwmUser'),
                                                        'source': '基础词',
                                                        'exStatus': tempLine['status']
                                                    }]
                                                    self.axios({
                                                            method: 'post',
                                                            url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                                                            data: xdata
                                                        })
                                                        .then(() => {
                                                            //console.log('添加到 无效词成功!')

                                                            // 然后哦，更改 在基础词中的状态
                                                            self.changeBasicWordStatus(tempLine['id'], '无效')
                                                        })
                                                        .catch(err => {
                                                            //console.log(err)
                                                            self.$Message.error(err.response.data.detail);
                                                            self.changeBasicWordStatus(tempLine['id'], '无效')
                                                        })

                                                })
                                                .catch((err) => {
                                                    console.log(err);
                                                    self.$Message.error("删除失败");
                                                });
                                            //},
                                            //onCancel: () => {
                                            //    console.log('取消添加!')
                                            //    //this.$Message.info('已取消');
                                            //    return
                                            //}
                                            //});
                                        } else {
                                            // 不存在于用户词典中
                                            // 那么，接下来直接往 无效词典里面插入，不管存不存在，如果存在，会自动报错跳过
                                            // 然后，将该词添加到 无效词
                                            //console.log('不存在于 用户词典中')
                                            let xdata = [{
                                                'word': tempLine['word'],
                                                'operator': localStorage.getItem('kwmUser'),
                                                'source': '基础词',
                                                'exStatus': tempLine['status']
                                            }]
                                            self.axios({
                                                    method: 'post',
                                                    url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                                                    data: xdata
                                                })
                                                .then(() => {
                                                    //console.log('添加到 无效词成功!')

                                                    // 然后哦，更改 在基础词中的状态
                                                    self.changeBasicWordStatus(tempLine['id'], '无效')
                                                })
                                                .catch(err => {
                                                    //console.log(err)
                                                    self.$Message.error(err.response.data.detail);
                                                    self.changeBasicWordStatus(tempLine['id'], '无效')
                                                })

                                        }
                                    })
                                    .catch(err => {
                                        console.log(err)
                                    })
                            }
                        })
                        .catch(err => {
                            console.log(err)
                        })

                }
            }
        },
        handleSelectRow: function () {
            this.selectedItemList = this.$refs.table.getSelection()
            // console.log('this.selectedItemList', this.selectedItemList)
        },
        fetchItems: function (getParams) {
            let self = this
            self.tableLoading = true
            let Params = getParams
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'basicWords/' + self.currentComponent,
                    params: Params
                })
                .then(res => {
                    // console.log(res)
                    // self.currentPage = 1
                    self.tableLoading = false
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.basicWordsItemData = res.data.content
                    self.dbName = res.data.dbName
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        fetchItemsES: function (getParams) {
            let self = this
            self.tableLoading = true
            let Params = getParams
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'basicWords/es/' + self.currentComponent,
                    params: Params
                })
                .then(res => {
                    // console.log(res)
                    // self.currentPage = 1
                    self.tableLoading = false
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.basicWordsItemData = res.data.content
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        handleFilter: function (column) {
            // 处理 分类,状态,长度，权重 筛选 ,帅选重置 的时候 也是这个 函数
            // console.log(column)
            let self = this
            let chekced = {
                'key': column['key'],
                'checked': column['_filterChecked']
            }
            //console.log('checked', chekced)
            if (chekced.key === 'category') {
                self.categoryChecked = chekced['checked']
            } else if (chekced.key === 'status') {
                self.statusChecked = chekced['checked']
            } else if (chekced.key === 'Length') {
                self.lengthChecked = chekced['checked']
            } else if (chekced.key === 'weight') {
                self.weightChecked = chekced['checked']
            }

            //重新筛选，激发重新搜索  ，包含 状态 和 分类. 此时 包含的查询参数  必须有: currentPage, pageSize, 可能有: urlPart,categoryFilter ,statusFilter

            self.currentPage = 1
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'dateRange':encodeURIComponent(self.dateRange),'urlPart':self.searchItem.toLowerCase() ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'statusFilter': encodeURIComponent(self.statusChecked)}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'basicWordItemId': '',
                'dateRange': encodeURIComponent(self.dateRange),
                'wordPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'lengthFilter': encodeURIComponent(self.lengthChecked),
                'weightFilter': encodeURIComponent(self.weightChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }
            self.fetchItemsES(Params)

        },
        pageChange: function (pageIndex) {
            // console.log(pageIndex)
            let self = this
            self.currentPage = pageIndex
            // let Params = {'currentPage':this.currentPage,'pageSize':this.pageSize}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'basicWordItemId': '',
                'dateRange': encodeURIComponent(self.dateRange),
                'wordPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'lengthFilter': encodeURIComponent(self.lengthChecked),
                'weightFilter': encodeURIComponent(self.weightChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }
            self.fetchItemsES(Params)
        },
        pageSizeChange: function (pageSize) {
            let self = this
            self.pageSize = pageSize
            self.currentPage = 1
            // console.log(pageSize)
            // let Params = {'currentPage':this.currentPage,'pageSize':this.pageSize}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'basicWordItemId': '',
                'dateRange': encodeURIComponent(self.dateRange),
                'wordPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'lengthFilter': encodeURIComponent(self.lengthChecked),
                'weightFilter': encodeURIComponent(self.weightChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }
            self.fetchItemsES(Params)
        },
        deleteConfirm: function () {
            let self = this
            // 当没有选项被选中时，不进行该操作
            if (self.selectedItemList.length === 0) {
                //console.log('no delete')
                self.$Message.info('无待删除项');
            } else {
                self.$Modal.confirm({
                    title: '删除确认',
                    content: '<p>删除后不可恢复,如果确定删除,请确认</p>',
                    onOk: () => {
                        this.deleteItems()
                    },
                    onCancel: () => {
                        //this.$Message.info('已取消');
                    }
                });
            }
        },
        deleteItems: function () {
            let self = this
            // 目前只需要把 每一行对应的uid取出来，发送到后端进行删除就好了
            // console.log(this.selectedItemList)
            let uids = []
            for (let element in self.selectedItemList) {
                uids.push(self.selectedItemList[element]['_id']['$oid'])
            }
            //console.log(uids)
            self.axios({
                    method: 'delete',
                    url: self.baseurl + 'basicWords/' + self.currentComponent,
                    data: uids
                })
                .then(() => {
                    setTimeout(()=>{self.batchSearch(self.basicWord)},2000)
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        TimeChange: function (daterange) {
            let self = this
            //console.log('time changed')
            //console.log(daterange)
            self.dateRange = daterange

            //日期被重新筛选，激发重新搜索
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'dateRange':encodeURIComponent(self.dateRange),'basicWordItemId': '','wordPart':self.searchItem.toLowerCase() ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'statusFilter': encodeURIComponent(self.statusChecked)}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'basicWordItemId': '',
                'dateRange': encodeURIComponent(self.dateRange),
                'wordPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'lengthFilter': encodeURIComponent(self.lengthChecked),
                'weightFilter': encodeURIComponent(self.weightChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }
            self.fetchItemsES(Params)
        },
    }
}
</script>

<style scoped>
>>>.ivu-table-cell {
    padding: 5px !important
}

.search-time-range {
    display: flex
}

>>>.basicWords-table tbody {
    font-weight: 450
}

.dragable-warp {

    padding: 3px 0px;
    display: flex;
    border-radius: 5px;
}

.dragablex {
    height: 32px;
    display: flex;
    border: 1px solid red;
    margin-left: 5px;
    border-radius: 5px;
    padding: 5px 0px;
    background-color: #057009;
    color: #fff;
    cursor: move;
    align-items: center;
    justify-content: space-between
}

.basicWords-button-group2 {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 5px;
    max-height: 550px;
    over-flow: auto
}

.label {
    margin-right: 10px;
}

.p0,
.p1,
.p2,
.p3 {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
    justify-content: space-between
}

.heihei {
    margin-left: 10px
}

>>>.ivu-table-fixed-header thead tr th, >>>.ivu-table-header thead tr th {
    border-bottom: 10px solid #e8eaec !important
}
</style>
