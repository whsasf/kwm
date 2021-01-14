<template>
<div>
    <div class="basicWords-button-group">
        <div class="x11">
            <div class="p0">
                <i-button type="error" icon="md-trash" @click="deleteConfirm">删除</i-button>
                <i-draggable class="dragable-warp" v-model="sortItems" @start="drag=true" @end="drag=false" @change="onChange">
                    <div class="dragablex" v-for="(item,index) in sortItems" :key="index">
                        <div class="label">{{item.name}}</div>
                        <i-select v-model="item.model" style="width:65px" @on-change="onChange">
                            <i-option v-for="item2 in sortList" :value="item2.value" :key="item2.value">{{ item2.label }}</i-option>
                        </i-select>
                    </div>
                </i-draggable>
                
            </div>
            <div class="p1">
                <i-button class="basicWords-export-button" type="warning" @click="exportDataX">
                    <i-icon type="md-download"></i-icon> 导出数据
                </i-button>
                <i-button class="download-Template" type="primary" @click="downloadTemplate">
                    <i-icon type="md-copy"></i-icon>下载模板
                </i-button>
            </div>
        </div>

        <div class="x22">
            <div class="p2">
                <i-button style="color: #fff;background-color: #54616f" @click="setStopWord">设为停止词</i-button>
                <i-button class="heihei" type="primary" icon="md-add-circle" @click="addItem">在线添加</i-button>

            </div>

            <div class="p3">
                <i-button style="color: #fff;background-color: #7b5ae4" @click="setInvalidWord">设为无效词</i-button>
                <i-upload class="heihei" ref="upload" action="" :show-upload-list="false" :before-upload="handleBeforeUpload">
                    <i-button type="primary" icon="md-cloud-upload" @click="addItems">批量添加</i-button>
                </i-upload>

            </div>
        </div>
        <div class="x33">
            <i-button v-if="expandStatus === 'finished' || expandStatus === ''" style="height: 70px; font-size: 30px;color: #fff;background-color: #057009" onMouseOver="this.style.color='#b6f204'" onMouseOut="this.style.color='#fff'" icon="md-power" @click="runExpand">拓词</i-button>
            <i-button v-else type="primary" style="height: 70px; font-size: 30px;color: #fff;background-color: #9ea4a9" :disabled="true">正在拓词...</i-button>
        </div>
    </div>
    <i-page :total="itemCount" :current="currentPage" placement="bottom" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />
    <i-table class="basicWords-table" :columns="columns1" :data="basicWordsItemData" :loading="tableLoading" @on-selection-change="handleSelectRow()" ref="table" stripe border @on-filter-change="handleFilter" @on-sort-change="handleSort">
        <template slot-scope="{ row,index }" slot="action">
            <div>
                <i-button type="warning" size="small" style="margin-right: 5px" @click="seeExpandTree(row,index)">查看拓词树</i-button>
                <i-button type="primary" size="small" style="margin-right: 5px" @click="editItem(row)">修改</i-button>
                <!--
                <router-link target="_blank" :to="{path:'/Project/' + currentComponent + '/basicWords'}">
                -->
                <i-button type="success" @click="seeNearWords(row.word)" size="small" style="margin-right: 5px">查看临近词语</i-button>
                <!-- </router-link> -->
            </div>
        </template>
    </i-table>
    <i-page :total="itemCount" :current="currentPage" placement="top" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />

    <!--弹出框都在此地-->
    <i-basicWordItemPage :key="refreshFlag" :rawCategories="rawCategories" :formCustom2="JSON.parse(JSON.stringify(formCustom))" :basicWordItemShow.sync="basicWordItemShow" @createBasicWords="createBasicWords" @deletebasicWordItem="handleDeleteBasicWordItem" @UpdateBasicWords="handleUpdateBasicWordItem"></i-basicWordItemPage>
    <i-checkSource :key="checkSourceKey" :dataRequired="dataRequired" :checkSourceShow.sync="checkSourceShow"></i-checkSource>
    <i-topoTree :treeType="treeType" :topoTreeKeyWord="topoTreeKeyWord" :key="topoTreeKey" :topoTreeShow.sync="topoTreeShow"></i-topoTree>
    <i-exportData :key="expordDataKey" :pageSize="pageSize" :selectedFlag="selectedFlag" :selected1="selected1" :pageData2Export="pageData2Export" :exportWindowShow.sync="exportWindowShow"></i-exportData>
    <i-similarWords :key="sikey" :similarShow2.sync="similarShow" :basicWord="basicWord" :categories="projetcCategoriesList"></i-similarWords>
</div>
</template>

<script>
import {
    mapState,
    mapMutations
} from 'vuex'
import basicWordItemPage from '@/components/basicWords/basicWordItemPage.vue'
import basicWordSearch from '@/components/basicWords/basicWordSearch.vue'
import checkSource from '@/components/basicWords/checkSource.vue'
import topoTree from '@/components/topoTree.vue'
import exportData from '@/components/basicWords/exportData.vue'
import similarWords from '@/components/basicWords/similarWords.vue'

export default {
    name: 'basicWords',
    data() {
        var global = this // 如果不这样， render 中找不到 正确的 this
        return {
            sikey: 4000,
            similarShow: false,
            basicWord: '',
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
            toStopConfirmShow: false,
            selectedFlag: [],
            expordDataKey: -20,
            pageData2Export: [],
            exportWindowShow: false,
            excelNoteData: [
                ['', '使用前必看！'],
                ['', ''],
                [1, '请将数据按照示例格式填写在basicWords sheet中'],
                [2, '不要修改basicWords sheet的名称，否则会出错'],
                [3, '不要使用中文逗号等分隔符'],
                [4, '从第3行开始写'],
                [5, '当前可选的目录。填写的未在可选目录中的目录,会被忽略掉，此处小心'],
                []
            ],
            excelTemplateData: {
                data: [
                    ["word", "category"],
                    ["", ""],
                    ["你好", "分类1,分类2,分类3,分类4,分类5,分类6"],
                    ["世界", "分类1,分类2,分类3,分类6"]
                ]
            },
            // topoTreeData: {},
            showReturn: [], // 期待返回的字段，为空则全部返回
            treeType: 'basic',
            topoTreeKeyWord: '',
            topoTreeShow: false,
            topoTreeKey: 200,
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
            refreshFlag: 1000,
            basicWordItemShow: false,
            selectedItemList: [],
            rawCategories: [],
            projetcCategoriesList: [],
            formCustom: {},
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
                    title: '基础词',
                    key: 'word',
                    align: 'center',
                    fixed: 'left',
                    minWidth: 120,
                    resizable: true,
                    renderHeader(h) {
                        return h('span', [
                            h('span', '基础词'),
                            h('i-poptip', {
                                    props: {
                                        title: "基础词全文搜索",
                                        content: "content",
                                        placement: "right-start",
                                        transfer: true,
                                        trigger: 'click',
                                        closable: true,
                                        width: 400,
                                        'word-wrap': true
                                    },
                                    //style:{ 'margin-left':'5px', 'color':'#057009', 'cursor':'pointer'}
                                    style: {
                                        'margin-left': '5px',
                                        'color': (() => {
                                            if (global.searchItem) {
                                                return '#2d8cf0'
                                            } else {
                                                return '#c5c8ce'
                                            }
                                        })(),
                                        'cursor': 'pointer'
                                    }
                                },
                                [h('i-icon', {
                                        props: {
                                            type: 'md-search',
                                            size: 20
                                        }
                                    }),
                                    h(basicWordSearch, {
                                        slot: "content",
                                        on: {
                                            'single-search': (item) => {
                                                // console.log(data)
                                                global.singleSearch(item)
                                                global.searchItem = item

                                            },
                                            'sync-query': (data) => {
                                                global.searchItem = data
                                            },
                                            'batch-search': (urlItem) => {
                                                //console.log('vvv',urlItem)
                                                global.batchSearch(urlItem)
                                                global.searchItem = urlItem
                                            },
                                            'reset-input': () => {
                                                global.resetInput()
                                            }
                                        }
                                    })
                                ]
                            )
                        ])
                    }

                },
                {
                    title: '分类',
                    key: 'category',
                    align: 'center',
                    minWidth: 200,
                    resizable: true,
                    filters: [],
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

                    },
                     filterMultiple: true,
                     renderHeader(h){
                        return h('span',[ 
                        h('span', '分类'),
                        ])
                    },
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
                    resizable: true,
                    renderHeader(h) {
                        return h('span', [
                            h('span', '生成时间'),
                            h('i-poptip', {
                                    props: {
                                        title: "日期过滤",
                                        content: "content",
                                        placement: "left-start",
                                        transfer: true,
                                        trigger: 'click',
                                        width: 400
                                    },
                                    style: {
                                        'margin-left': '5px',
                                        'color': (() => {
                                            if (global.dateRange.length === 2 && global.dateRange[0] === '' && global.dateRange[1] === '') {
                                                return '#c5c8ce'
                                            } else {
                                                return '#2d8cf0'
                                            }
                                        })(),
                                        'cursor': 'pointer'
                                    }
                                },
                                [h('i-icon', {
                                        props: {
                                            type: 'ios-funnel',
                                            size: 16
                                        }
                                    }),
                                    h('i-datePicker', {
                                        slot: "content",
                                        props: {
                                            type: 'datetimerange',
                                            placeholder: '选择日期时间区间',
                                            transfer: false,
                                            format: "yyyy/MM/dd HH:mm:ss"
                                        },
                                        style: {
                                            position: 'static',
                                            width: '320px'
                                        },
                                        on: {
                                            'on-change': (daterange) => {
                                                // console.log(daterange)
                                                global.TimeChange(daterange)
                                            }
                                        }
                                    })
                                ])
                        ])
                    }
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
                    // render: (h, params) => {
                    //   // console.log(params.row)
                    //       return (h('p',params.row.splitWords.join(';')))
                    //   }
                },
                {
                    title: '操作',
                    key: 'action',
                    slot: 'action',
                    align: 'center',
                    width: 280,
                    resizable: true
                }
            ],
        }
    },
    computed: {
        ...mapState(['baseurl', 'currentComponent','expandAddr']),
    },
    components: {
        'i-basicWordItemPage': basicWordItemPage,
        'i-checkSource': checkSource,
        'i-topoTree': topoTree,
        'i-exportData': exportData,
        'i-similarWords': similarWords
    },
    mounted() {
        // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize}
        // this.loading = true
        let self = this
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
        self.fetchItems(Params)
        self.fetchProjectCategories();
        self.fetchExpandStatus()
    },
    methods: {
        ...mapMutations(['changeSearchDisplay']),
        fetchExpandStatus: function () {
            let self = this
            // 服务端获取 最近一次任务 id 及 状态
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'basicWords/expandMission/' + self.currentComponent,
                })
                .then(res => {
                    //console.log(res)
                    if (res.data.count > 0) {
                        let taskID = res.data.content[0].taskID
                        self.expandStatus = res.data.content[0].status
                        // 如果状态时 未完成，则 获取最新状态，否则，不获取
                        if (self.expandStatus === 'unknown') {
                            // 获取状态
                            self.axios({
                                    method: 'get',
                                    url: self.expandAddr + 'spider/status/' + taskID,
                                })
                                .then(res => {
                                    //console.log(res)
                                    if (res.data.status === 'success') {
                                        self.expandStatus = res.data.data.status
                                        //console.log(this.crawlerStatus)
                                        // 如果已完成，将状态 同步到 服务端  crawlerMission
                                        if (self.expandStatus === 'finished') {

                                            // 更新 crawler mission 状态
                                            self.axios({
                                                    method: 'patch',
                                                    url: self.baseurl + 'basicWords/expandMission/' + self.currentComponent + '/' + taskID,
                                                    params: {
                                                        'status': 'finished'
                                                    }
                                                })
                                                .then(() => {
                                                    //console.log('拓词任务完成状态，更新到服务端成功!')
                                                    // 激发 母词 计算，仅计算 当前

                                                })
                                                .catch(err => {
                                                    console.log(err)
                                                })
                                        }
                                    } else {
                                        self.crawlerStatus = ''
                                    }

                                })
                                .catch(err => {
                                    console.log('err', err)
                                })
                        }
                    }
                })
                .catch(err => {
                    console.log('err', err)
                })

        },
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
        downloadTemplate: function () {
            // 向 excelNoteData 中添加 目录数据
            let xx = JSON.parse(JSON.stringify(this.rawCategories))
            xx.unshift('') //
            this.excelNoteData[7] = xx
            let worksheet1 = this.$XLSX.utils.aoa_to_sheet(this.excelNoteData)
            let worksheet2 = this.$XLSX.utils.aoa_to_sheet(this.excelTemplateData.data)
            let new_workbook = this.$XLSX.utils.book_new()
            this.$XLSX.utils.book_append_sheet(new_workbook, worksheet1, "说明")
            this.$XLSX.utils.book_append_sheet(new_workbook, worksheet2, "basicWords")
            this.$XLSX.writeFile(new_workbook, 'basicWords-template.xlsx')
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
        getRandomColor: function Color() {
            // 生成随机的颜色
            var r = Math.floor(Math.random() * 255).toString(16);
            var g = Math.floor(Math.random() * 255).toString(16);
            var b = Math.floor(Math.random() * 255).toString(16);
            r = r.length == 1 ? "0" + r : r;
            g = g.length == 1 ? "0" + g : g;
            b = b.length == 1 ? "0" + b : b;
            return "#" + r + g + b;
        },
        singleSearch: function (uid) {
            // search item with specifif uid ,so only one will return
            let self = this
            // console.log('singleSearch')
            //self.searchItem = ''
            self.changeSearchDisplay(uid[1])
            //console.log('uid', uid)
            //console.log('searchItem', self.searchItem)
            self.searchResult = [] //disapper options window
            // 当进行 single search的时候，因为只关注一条记录，所以，其他筛选项是被忽略的，不发送它们

            self.currentPage = 1
            let Params = {
                'currentPage': 1, //self.currentPage,
                'pageSize': self.pageSize,
                'basicWordItemId': uid[0]
            }
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'UrlId': item['_id']['$oid']}
            self.fetchItems(Params)
        },
        resetInput: function () {
            let self = this
            //console.log('reset input')
            self.searchItem = ''
            self.searchResult = []
            self.changeSearchDisplay('')

            //url输入 被重新筛选 为空 ，激发重新搜索（完全搜索）
            let Params = {
                'currentPage': 1,
                'pageSize': self.pageSize
            }
            self.fetchItems(Params)
        },
        basicWordsSearch: function () {
            // 实时查询候选 选项
            // 选择特定条目时的动作: 进入 singleSearch
            let self = this
            let query = self.searchItem
            // console.log(query)
            // self.searchItem = query.toLowerCase()
            //console.log(this.searchItem)
            //发往后端，进行查询,如果 query 不为空 
            if (query !== '') {
                // let Params = {'urlPart':query.toLowerCase()}
                // 全部返回，所以 页面设置 为  0,0 
                // let Params = {'currentPage':0,'pageSize':0,'basicWordItemId': '','dateRange':encodeURIComponent(self.dateRange),'wordPart':self.searchItem.toLowerCase() ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'statusFilter': encodeURIComponent(self.statusChecked),'lengthFilter': encodeURIComponent(self.lengthChecked),'weightFilter': encodeURIComponent(self.weightChecked)}
                let Params = {
                    'currentPage': 0,
                    'pageSize': 0,
                    'basicWordItemId': '',
                    'dateRange': encodeURIComponent(self.dateRange),
                    'wordPart': self.searchItem.toLowerCase(),
                    'categoryFilter': encodeURIComponent(self.categoryChecked),
                    'statusFilter': encodeURIComponent(self.statusChecked),
                    'lengthFilter': encodeURIComponent(self.lengthChecked),
                    'weightFilter': encodeURIComponent(self.weightChecked),
                    'sortDict': JSON.stringify(self.sortDict)
                }
                // self.fetchItems(Params)
                self.axios({
                        method: 'get',
                        url: self.baseurl + 'basicWords/es/' + self.currentComponent,
                        params: Params
                    })
                    .then(res => {
                        // console.log(res)
                        // if (res.data.count !== ''){
                        //   self.projectCount = res.data.count
                        // }
                        self.searchResult = res.data.content
                        // console.log(self.searchResult)
                    })
                    .catch(err => {
                        console.log(err)
                        // self.$Message.error(err.response.data.detail);
                    })
            } else {
                self.searchResult = []
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
            self.changeSearchDisplay(part)
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
                .then(res => {
                    // console.log(res)
                    // self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.basicWordsItemData = res.data.content
                    self.selectedItemList = []
                    return
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
        handleUpdateBasicWordItem: function (data2Update) {

            let self = this

            let pageParams = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            //console.log('mmm', pageParams, data2Update)
            self.axios({
                    method: 'patch',
                    url: self.baseurl + 'basicWords/' + self.currentComponent + '/' + data2Update.uid,
                    data: data2Update.data,
                    params: pageParams
                })
                .then(res => {
                    // console.log(res)
                    // self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.basicWordsItemData = res.data.content
                })
                .catch(err => {
                    // console.log(err)
                    //console.log(err.response.data.detail)
                    self.$Message.error(err.response.data.detail);
                })
        },
        handleDeleteBasicWordItem: function (uidInfo) {
            let self = this
            let uid = uidInfo['uid']
            // 联系后台，进行删除
            self.axios({
                    method: 'delete',
                    url: self.baseurl + 'basicWords/' + self.currentComponent,
                    data: [uid]
                })
                .then(res => {
                    // console.log(res)
                    self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.basicWordsItemData = res.data.content
                })
                .catch(err => {
                    // console.log(err)
                    console.log(err.response.data.detail)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        seeExpandTree: function (row) {
            let self = this
            //console.log(row.word, index)
            self.topoTreeKeyWord = {
                'kword': row.word,
                'status': row.status
            } // 要把状态带上，后端好统一出出力
            // self.topoTreeKey --
            self.topoTreeKey--
            self.topoTreeShow = true
        },
        editItem: function (row) {
            let self = this
            // console.log(row,index)
            self.formCustom = {}
            self.$set(self.formCustom, 'uid', row['_id']['$oid'])
            self.$set(self.formCustom, 'Items', [{
                'value': {
                    'word': row.word,
                    'category': row.category,
                    'source': row.source.join(','),
                    // 'index': 1,
                    'status': row.status + ' (' + row.timestamp + ') '
                },
                // 'status': 1,
                // index: index + 1
            }])
            self.refreshFlag--
            self.basicWordItemShow = true
        },
        seeNearWords: function (word) {
            //console.log('你正在查看词' + word + '的临近次')
            let self = this
            self.basicWord = word
            self.similarShow = true
            self.sikey -= 1
        },
        handleSelectRow: function () {
            this.selectedItemList = this.$refs.table.getSelection()
            // console.log('this.selectedItemList', this.selectedItemList)
        },
        createBasicWords: function (data2Create) {
            //console.log(data2Create)
            let self = this
            self.axios({
                    method: 'post',
                    url: self.baseurl + 'basicWords/' + self.currentComponent,
                    data: data2Create
                })
                .then(res => {
                    self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.basicWordsItemData = res.data.content
                    //self.formCustom = self.formCustomOrigin
                })
                .catch(err => {
                    // console.log(err.response.data.detail)
                    //self.$Message.error(err.response.data.detail);
                    self.$Message.error({
                        content: JSON.stringify(err.response.data.detail),
                        duration: 0,
                        closable: true
                    });
                    //self.formCustom = self.formCustomOrigin
                })
        },
        fetchProjectCategories: function () {
            // 获取所有 该项目下的所有 目录列表
            let self = this
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Categories/' + self.currentComponent
                })
                .then(res => {
                    //console.log(res)
                    for (let ele in res.data.content) {
                        self.projetcCategoriesList.push({
                            'label': res.data.content[ele].categoryName,
                            'value': res.data.content[ele].categoryName
                        })
                        self.rawCategories.push(res.data.content[ele].categoryName)
                    }
                    // console.log('projetcCategoriesList',self.projetcCategoriesList)
                    self.columns1[3].filters = self.projetcCategoriesList // 必须要设置一下 ，目录列表
                    // console.log(self.rawCategories)
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
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
        runExpand: function () {
            // 真正开始托词
            let self = this
            if (self.selectedItemList.length === 0) {
                self.$Message.warning('未选择基础词!');
            } else {
                // 获取待 爬取的 语料 word 列表
                let basicWords = []
                for (let element in self.selectedItemList) {
                    basicWords.push(self.selectedItemList[element]['word'])
                }

                let configure = {
                    "id": "kms_tuoci",
                    "version": "1.4",
                    "params": {
                        //"mongo_path": "mongodb://root:root@114.67.113.229:8004",
                        "spider_name": "minions.demo14",
                        "mongo_ip": "114.67.113.229",
                        "mongo_username": "root",
                        "mongo_password": "root",
                        "mongo_port": "8004",
                        "mongo_db": self.dbName,
                        "mongo_collection": 'basicWords',
                        "query_field": "word",
                        "mongo_filter": basicWords,
                        "mongo_save_path": "mongodb://root:root@114.67.113.229:8004",
                        "mongo_save_db": self.dbName,
                        "mongo_save_collection": "extendedWords"
                    }
                }
                //console.log(configure, basicWords)
                // 发送  拓词 命令
                self.axios({
                        method: 'post',
                        headers: {
                            'content-type': 'application/json'
                        },
                        url: self.expandAddr + 'spider/call',
                        data: configure
                    })
                    .then(res => {
                        //console.log(res)
                        //console.log('托词返回值:', res)
                        // 将 托词 条件，拓取的数据，时间戳，哪个用户 拓的，以及 托词端返回的状态，保存到服务器端, 当前项目中的新表:  expandMission
                        let taskID = res.data.data.task
                        let expandInfo = {
                            'operator': localStorage.getItem('kwmUser'),
                            'taskID': taskID,
                            'targets': basicWords,
                            'status': 'unknown'
                        }
                        // 将 拓词 所有相关信息，保存在服务端
                        self.axios({
                                method: 'post',
                                url: self.baseurl + 'basicWords/expandMission/' + self.currentComponent,
                                data: expandInfo
                            })
                            .then(() => {
                                //console.log('拓词任务，保存在服务端成功!')
                                //5s后刷新 状态
                                //setTimeout(() => {
                                self.fetchExpandStatus()
                                //}, 5000)

                                //self.$Message.info('当前拓词源信息，已经保存到服务端!');
                            })
                            .catch(err => {
                                console.log(err)
                                //self.$Message.warning('当前拓词源信息，保存到服务端失败!');
                            })
                    })
                    .catch(err => {
                        console.log(err)
                    })
            }
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
        addItems: function () {
            // self.basicWordItemShow = true
            //console.log('addd items')

        },
        handleBeforeUpload: function (file) {
            // 批量上传
            let self = this
            // 判断 上传的文件是不是  excel文件，如果不是报错并退出
            let fileTypes = {
                'xlsx': '1',
                'xls': '1'
            }
            if (fileTypes[file.name.split('.')[1].toLowerCase()] !== '1') {
                self.$Message.error('文件类型必须是 xlsx 或 xls');
                return
            }
            let initFlag = 0 // 记录元素个数
            let temp = {
                // itemIndex: initFlag,
                uid: '',
                Items: []
            }
            // xlsx 组件解析 文件内容到 json
            let reader = new FileReader();
            reader.readAsArrayBuffer(file);
            reader.onload = function (e) {
                let data = new Uint8Array(e.target.result);
                let workbook = self.$XLSX.read(data, {
                    type: 'array'
                });
                // console.log('workbook-url',workbook.Sheets.basicWords)
                // 前一行是 header，所以略过。第二行是空行，空行在读的时候已经被 略过
                let dataFormat = self.$XLSX.utils.sheet_to_json(workbook.Sheets.basicWords, {
                    header: 1,
                    blankrows: false,
                    defval: '' // 空的项，读为 null
                }).slice(2)
                //console.log('dataFormat',dataFormat)
                for (let ele in dataFormat) {
                    let lineData = dataFormat[ele]

                    try {
                        initFlag++
                        let tempCategory = lineData[1].trim().replace(/，/g, ',').split(',')
                        let tempCategory2 = []
                        if (tempCategory[0] !== '') {
                            // 处理不在 目录列表的目录
                            for (let ele in tempCategory) {
                                if (self.rawCategories.includes(tempCategory[ele])) {
                                    tempCategory2.push(tempCategory[ele])
                                }
                            }
                        }
                        tempCategory = tempCategory2 // tempCategory = [] 或 只包含 有效值的 分类数组

                        temp.Items.push({
                            'value': {
                                'word': lineData[0].trim(),
                                'category': tempCategory, //lineData[1].trim().replace(/，/g, ',').split(','),
                                'source': '手动添加',
                                'status': ''
                            },
                            //'index': initFlag,
                            //'status': 1
                        })
                    } catch (error) {
                        self.$Message.error(error.message);
                    }
                }
                temp.itemIndex = initFlag
                self.formCustom = temp
                //console.log(self.formCustom)
                // 激活进入 编辑页面
                self.refreshFlag--
                self.basicWordItemShow = true
            }
            return false // 返回false 代表 不上传
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
                .then(res => {
                    // console.log(res)
                    self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.selectedItemList = []
                    self.basicWordsItemData = res.data.content
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        addItem: function () {
            let self = this
            self.formCustom = {
                    //itemIndex: 1,
                    uid: '',
                    Items: [{
                        value: {
                            'word': '',
                            'category': [],
                            'status': '待查询...',
                            'source': '手动添加'
                        }
                        //index: 1
                    }]
                },
                self.refreshFlag--
            self.basicWordItemShow = true
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

.basicWords-button-group {
    display: flex;
    align-items: center;
    margin-bottom: 5px
}

.x11 {
    flex: 3;
    justify-content: flex-start;
}

.x22 {
    margin-left: 50px;
    flex: 3;
    justify-content: flex-end
}

.x33 {
    margin-left: 20px;
    margin-bottom: 5px;
    justify-content: flex-end;
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
</style>
