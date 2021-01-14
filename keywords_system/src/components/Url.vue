<template>
<div class="Url">
    <div class="url-p">
            <i-button type="error" icon="md-trash" @click="deleteConfirm">删除</i-button>
            <i-button type="warning" @click="exportDataX()">
                <i-icon type="md-download"></i-icon> 导出数据
            </i-button>
            <i-button class="url-p21" type="primary" icon="md-add-circle" @click="addItem">手动添加</i-button>
            <i-upload class="url-p22" :format="['xlsx','xls']" ref="upload" action="" :show-upload-list="false" :before-upload="handleBeforeUpload">
                <i-button type="primary" icon="md-cloud-upload" @click="addItems">批量添加</i-button>
            </i-upload>
            <i-button class="url-p23" type="primary" @click="downloadTemplate" icon="md-copy">下载模板</i-button>
            <i-button class="url-p24" type="warning" @click="drawerShow.show = !drawerShow.show" icon="md-copy">数据中转站</i-button>
            <i-button v-if="crawlerStatus === 'finished' || crawlerStatus === ''" class="url-p25" height="200" style="color: #fff;background-color: #057009" onMouseOver="this.style.color='#b6f204'" onMouseOut="this.style.color='#fff'" icon="md-power" @click="runcrawler(selectedTotal)">开始爬取</i-button>
            <i-button v-else type="primary" style="color:#494c50" :disabled="true">正在爬取...</i-button>
    </div>
    <i-page :total="itemCount" :current="currentPage"  placement="bottom" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />
    <i-table class="Url-table" :columns="columns1" :data="UrlItemData" :loading="loading" @on-selection-change="handleSelectRow()" ref="table" stripe border @on-filter-change="handleFilter">
        <template slot-scope="{ row,index }" slot="action">
            <div class="Url-actions">
                <i-button type="primary" size="small" style="margin-right: 5px" @click="Urledit(row)">编辑</i-button>
                <i-button type="success" size="small" style="margin-right: 5px" @click="seeUrlDetail(row,index)">检视</i-button>
                <i-button v-if="row.status==='无效'" type="success" size="small" shape="circle" @click="tagValid({'uid':row['_id']['$oid']})">设为有效</i-button>
                <i-button v-else-if="row.status==='未开始'" type="primary" shape="circle" size="small" @click="runcrawler([{'url':row.rootUrl}])">开始</i-button>
                <i-button v-else-if="row.status==='成功'" type="success" shape="circle" size="small" @click="UrlAction(row)">查看结果</i-button>
                <i-button v-else-if="row.status==='失败'" type="warning" shape="circle" size="small" @click="UrlAction(row)">重新开始</i-button>
                <i-button v-else-if="row.status==='爬取中'" disabled shape="circle" type="default" size="small" @click="UrlAction(row)">等待</i-button>
            </div>
        </template>
    </i-table>
    <br>
    <i-page :total="itemCount" :current="currentPage" placement="top" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />

    <!-- 隐藏组件在此-->
    <i-itemPage :key="xyz" :rowCategoies="rowCategoies" :formCustom2="JSON.parse(JSON.stringify(formCustom))" :urlItemWindowShow.sync="urlItemWindowShow" :urlItemPageTitle="urlItemPageTitle" @createUrlNewItem="handleUrlNewItem" @deleteUrlNewItem="handleUrlDeleteItem"></i-itemPage>
    <i-seeDetail :DetailWindowShow2.sync="DetailWindowShow" :currentPageNum="currentPage" :totalPageNum="Math.ceil(itemCount/pageSize)" :detailIndex="detailIndex" :pageData="UrlItemData" :key="seeDetailKey" @tagInvalid="tagInvalid" @tagValid="tagValid" @askForPrePage="fetchPrevPage" @askForNextPage="fetchNextPage"></i-seeDetail>
    <i-exportData :key="expordDataKey" :pageSize="pageSize" :selectedFlag="selectedFlag" :selected1="selected1" :pageData2Export="pageData2Export" :exportWindowShow.sync="exportWindowShow"></i-exportData>
    <i-dataHouse @click.stop="drawerShow=!userClick" @reset="resetDataHouse" @updateSelectedOldUrlsList="updateSelectedOldUrlsList" :xdata.sync="selectedTotal" :drawerShow.sync="drawerShow"></i-dataHouse>

    <!-- loading-->
    <div v-if="showLoading" class="demo-spin-col" span="8">
        <i-spin fix>
            <i-icon type="ios-loading" size=18 class="demo-spin-icon-load"></i-icon>
            <div>Loading</div>
        </i-spin>
    </div>

</div>
</template>

<script>
import {
    mapState,
    mapMutations
} from 'vuex'
// import XLSX from 'xlsx';
import itemPage from '@/components/Urls/urlItemPage.vue'
import seeDetail from '@/components/Urls/seeDetails.vue'
import urlSearch from '@/components/Urls/urlSearch.vue'
import exportData from '@/components/Urls/exportData.vue'
import dataHouse from '@/components/Urls/dataHouse.vue'
export default {
    name: 'Url',
    data() {
        var global = this // 如果不这样， render 中找不到 正确的 this
        return {
            crawlerStatus: '',
            userClick: false,
            //crowlerAddr: 'http://114.67.113.229:8006/spider/call',
            //crowlerAddr: 'http://192.168.20.85:8000/',
            dbName: '', // 当前项目 所在的  mongo 数据库 名称
            drawerShow: {
                'show': false
            }, // 设置关键词 抽屉显示
            selectedTotal: [],
            selectedOldUrlsList: [], // 仅 存储 selectedOldFull 中 url 列表，方便进行 重复 判断
            selectedOldFull: [], // 所有选中的uel 及其他信息 列表,当前页的除外。因为当前页的可以反复选中以及取消选中，当前页的用系统的 selectedItemList
            showLoading: false,
            exportWindowShow: false,
            expordDataKey: 200,
            pageData2Export: [],
            selected1: '当前选中',
            selectedFlag: [],
            excelNoteData: [
                ['', '使用前必看！'],
                ['', ''],
                [1, '请将数据按照示例格式填写在Urls sheet中'],
                [2, '不要修改Utls sheet的名称，否则会出错'],
                [3, '不要使用中文逗号等分隔符'],
                [4, '路径载入方式从 regex 和 包含 中二选一'],
                [5, '从第3行开始写'],
                [6, '当前可选的目录。填写的未在可选目录中的目录,会被忽略掉，此处小心'],
                []
            ],
            excelTemplateData: {
                data: [
                    ["Url(必填)", "允许路径", "允许路径类型(regex 和 包含 二选一)", "排除路径", "排除路径类型regex 和 包含 二选一", "分类(相同Url,分类相同,可以只写第一个,或者全写.英文逗号分隔)"],
                    ["", "", "", "", "", ""],
                    ["https://www.baidu.com", "https://www.baidu.com/include1", "regex", "https://www.baidu.com/exclude1", "regex", ""],
                    ["https://www.baidu.com", "https://www.baidu.com/include2", "包含", "https://www.baidu.com/exclude2", "regex", ""],
                    ["https://www.baidu.com", "https://www.baidu.com/include3", "regex", "https://www.baidu.com/exclude3", "包含", ""],
                    ["https://www.stockhey.com", "https://www.stockhey.com/include1", "regex", "https://www.stockhey.com/exclude1", ""],
                    ["https://www.stockhey.com", "https://www.stockhey.com/include2", "包含", "https://www.stockhey.com/exclude2", "regex", ""]
                ]
            },
            xyz: 1000,
            searchReaultListvisible: true,
            searchItem: '',
            seeDetailKey: 0,
            DetailWindowShow: false,
            // website: 'https://www.stockhey.com',
            detailIndex: 0,
            searchResult: [],
            okData: [],
            badData: [],
            selectedItemList: [],
            categoryChecked: [],
            statusChecked: [],
            dateRange: ['', ''],
            loading: false,
            itemCount: 0,
            currentPage: 1,
            pageSize: 10,
            select3: 'Url',
            projetcCategoriesList: [],
            rowCategoies: [],
            urlItemPageShow: false,
            urlItemWindowShow: false,
            urlItemPageTitle: '单条添加',
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
                    title: 'Url',
                    key: 'rootUrl',
                    align: 'left',
                    minWidth: 200,
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params)
                        return h('a', {
                            on: {
                                click: () => {
                                    window.open(params.row.rootUrl)
                                }
                            }
                        }, params.row.rootUrl)
                    },
                    renderHeader(h) {
                        return h('span', [
                            h('span', 'Url'),
                            h('i-poptip', {
                                    props: {
                                        title: "URL过滤",
                                        content: "content",
                                        placement: "top",
                                        transfer: true,
                                        trigger: 'click',
                                        width: 450,
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
                                    h(urlSearch, {
                                        slot: "content",
                                        on: {
                                            'single-search': (item) => {
                                                // console.log(data)
                                                global.singleSearch(item)

                                            },
                                            'sync-query': (data) => {
                                                global.searchItem = data
                                            },
                                            'batch-search': (urlItem) => {
                                                //console.log('vvv',urlItem)
                                                global.batchSearch(urlItem)
                                            },
                                            'reset-input': () => {
                                                global.resetInput()
                                            }
                                        }
                                    })
                                ]
                            )
                        ])
                    },
                    fixed: 'left',
                },
                {
                    title: '允许路径',
                    key: 'urlIncludePath',
                    align: 'left',
                    minWidth: 200,
                    resizable: true,
                    render: (h, params) => {
                        return params.row.urlIncludePath.map((data, index) => {
                            //console.log(data.path)
                            //return h('p', data.path + '[' + data.type + ']')
                            return h('div', [
                                h('span', {
                                    style: {
                                        color: '#212891'
                                    },
                                }, '(' + (parseInt(index) + 1) + ') '),
                                h('span', data.path),
                                h('span', {
                                    style: {
                                        color: '#057009'
                                    },
                                }, '[' + data.type + ']')
                            ])
                        })
                    }

                },
                {
                    title: '排除路径',
                    key: 'urlExcludePath',
                    align: 'left',
                    minWidth: 200,
                    resizable: true,
                    render: (h, params) => {
                        return params.row.urlExcludePath.map((data, index) => {
                            //console.log(data.path)
                            //return h('p', data.path + '[' + data.type + ']')
                            return h('div', [
                                h('span', {
                                    style: {
                                        color: '#212891'
                                    },
                                }, '(' + (parseInt(index) + 1) + ') '),
                                h('span', data.path),
                                h('span', {
                                    style: {
                                        color: '#057009'
                                    },
                                }, '[' + data.type + ']')
                            ])
                        })
                    }
                },
                {
                    title: '分类',
                    key: 'category',
                    align: 'left',
                    minWidth: 120,
                    filters: [],
                    filterMultiple: true,
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        //if (row.category.includes(value)){
                        return row //什么都不做，由专门的函数进行后端筛选
                        //}
                    },
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params.row)
                        //return (h('p', params.row.category.join(';')))
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
                    minWidth: 60,
                    filters: [{
                        'label': '无效',
                        'value': '无效'
                    }, {
                        'label': '未开始',
                        'value': '未开始'
                    }, {
                        'label': '爬取中',
                        'value': '爬取中'
                    }, {
                        'label': '成功',
                        'value': '成功'
                    }, {
                        'label': '失败',
                        'value': '失败'
                    }, ],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        //if (row.status === value){
                        return row //什么都不做，由专门的函数进行后端筛选
                        //}
                    },
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params)
                        if (params.row.status === '无效') {
                            return h('p', {
                                style: {
                                    'background-color': 'rgba(100, 108, 122, 0.5)',
                                }
                            }, params.row.status)
                        } else if (params.row.status === '未开始') {
                            return h('p', params.row.status)
                        } else if (params.row.status === '成功') {
                            return h('p', {
                                style: {
                                    'background-color': 'rgba(14, 237, 66, 0.5)',
                                }
                            }, params.row.status)
                        } else if (params.row.status === '失败') {
                            return h('p', {
                                style: {
                                    'background-color': 'rgba(237, 14, 40, 0.5)',
                                }
                            }, params.row.status)
                        } else if (params.row.status === '爬取中') {
                            return h('p', {
                                style: {
                                    'background-color': 'rgba(247, 239, 4, 0.5)',
                                }
                            }, params.row.status)
                        }

                    }
                },
                {
                    title: '变更时间',
                    key: 'modifiedTime',
                    align: 'center',
                    minWidth: 100,
                    resizable: true,
                    renderHeader(h) {
                        return h('span', [
                            h('span', '变更时间'),
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
                    title: '操作',
                    key: 'action',
                    slot: 'action',
                    align: 'center',
                    width: 150,
                    fixed: 'right',
                    resizable: true
                }
            ],
            UrlItemData: [],
            formCustom: {}
        }
    },
    computed: {
        ...mapState(['baseurl', 'currentComponent','crowlerAddr']),
    },
    created() {
        this.fetchAllItems() // 获取当前
    },
    components: {
        'i-itemPage': itemPage,
        'i-seeDetail': seeDetail,
        'i-exportData': exportData,
        'i-dataHouse': dataHouse
    },
    beforeMount() {},
    mounted() {
        // 获取所有 该项目下的所有 目录列表
        // console.log('mounted feytting categories')
        this.fetchProjectCategories();
        this.fetchCrawlerStatus()
        // 添加事件
        // document.addEventListener("click", this.handleOtherclick)
    },
    beforeDestroy() {
        this.$Message.destroy()
    },
    methods: {
        ...mapMutations(['changeSearchDisplay']),
        fetchCrawlerStatus: function () {
            let self = this
            // 服务端获取 最近一次任务 id 及 状态
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Urls/crawlerMission/' + self.currentComponent,
                })
                .then(res => {
                    //console.log(res)
                    if (res.data.content.length > 0) {
                        let taskID = res.data.content[0].taskID
                        self.crawlerStatus = res.data.content[0].status
                        //console.log('self.crawlerStatus', self.crawlerStatus)
                        // 如果状态时 未完成，则 获取最新状态，否则，不获取
                        if (self.crawlerStatus === 'unknown') {
                            // 获取状态
                            //console.log('去爬虫服务端获取最新状态...')
                            self.axios({
                                    method: 'get',
                                    url: self.crowlerAddr + 'spider/status/' + taskID,
                                })
                                .then(res => {
                                    //console.log('爬虫服务端最新状态' + JSON.stringify(res.data))
                                    if (res.data.status === 'success') {
                                        self.crawlerStatus = res.data.data.status
                                        //console.log(this.crawlerStatus, taskID)
                                        // 如果已完成，将状态 同步到 服务端  crawlerMission
                                        if (self.crawlerStatus === 'finished') {
                                            //console.log('爬虫任务已经成功，现在同步状态到服务端')
                                            // 更新 crawler mission 状态
                                            self.axios({
                                                    method: 'patch',
                                                    url: self.baseurl + 'Urls/crawlerMission/' + self.currentComponent + '/' + taskID,
                                                    params: {
                                                        'status': 'finished'
                                                    }
                                                })
                                                .then(() => {
                                                    //console.log('爬虫任务完成状态，更新到服务端成功!')

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
        updateSelectedOldUrlsList: function (url) {
            //console.log('deleted url', url)
            let urlIndex = this.selectedOldUrlsList.indexOf(url.trim())
            if (urlIndex !== -1) {
                // 存在，则对应删除
                this.selectedOldUrlsList.splice(urlIndex, 1)
            }
        },
        resetDataHouse: function () {
            this.selectedTotal = []
            this.selectedOldUrlsList = []
            this.selectedOldFull = []
            //this.selectedItemList = []
        },
        downloadTemplate: function () {
            // 向 excelNoteData 中添加 目录数据
            let xx = JSON.parse(JSON.stringify(this.rowCategoies))
            xx.unshift('')
            this.excelNoteData[8] = xx
            let worksheet1 = this.$XLSX.utils.aoa_to_sheet(this.excelNoteData)
            let worksheet2 = this.$XLSX.utils.aoa_to_sheet(this.excelTemplateData.data)
            let new_workbook = this.$XLSX.utils.book_new()
            this.$XLSX.utils.book_append_sheet(new_workbook, worksheet1, "说明")
            this.$XLSX.utils.book_append_sheet(new_workbook, worksheet2, "Urls")
            this.$XLSX.writeFile(new_workbook, 'Urls-template.xlsx')
        },
        handleOtherclick: function (e) {
            // 让下拉框， 在页面其他地方被点击的时候，消失
            if (this.$refs.urlInputOptions.contains(e.target)) {
                return
            } else {
                // console.log('out')
                this.searchResult = []
            }
        },
        fetchNextPage: function () {
            let self = this
            self.currentPage = this.currentPage + 1
            self.detailIndex = 0
            self.UrlItemData = []
            // self.seeDetailKey = self.seeDetailKey +1
            //self.fetchAllItems()

            // 获取全部 符合当前条件的数据
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'UrlId': '',
                'urlPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked)
            }
            self.fetchItemsES(Params)

        },
        fetchPrevPage: function () {

            let self = this
            self.currentPage = self.currentPage - 1
            self.detailIndex = self.pageSize - 1
            self.UrlItemData = []
            // self.seeDetailKey = self.seeDetailKey +1
            //self.fetchAllItems()

            // 获取全部 符合当前条件的数据
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'UrlId': '',
                'urlPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked)
            }
            self.fetchItemsES(Params)

        },
        fetchProjectCategories: function () {
            // 获取所有 该项目下的所有 目录列表
            let self = this
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Categories/' + self.currentComponent

                })
                .then(res => {
                    // console.log('vvvvvvvvv',res)
                    for (let ele in res.data.content) {
                        self.projetcCategoriesList.push({
                            'label': res.data.content[ele].categoryName,
                            'value': res.data.content[ele].categoryName
                        })
                        self.rowCategoies.push(res.data.content[ele].categoryName)
                    }
                    // 将 excel 模板中得到 分类，全部 默认设为 当前项目所有分类
                    for (let i = 2; i <= 6; i++) {
                        self.excelTemplateData.data[i][5] = self.rowCategoies.join(',')
                    }
                    //console.log('self.excelTemplateData', self.excelTemplateData)
                    //console.log('projetcCategoriesList', self.projetcCategoriesList)
                    self.columns1[5].filters = self.projetcCategoriesList // 必须要设置一下 ，目录列表
                    // console.log( self.rowCategoies)
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        tagValid: function (data) {
            // 将url 标记为 有效
            let self = this
            //console.log(data)
            let uid = data.uid

            let payLoad = {
                'status': '未开始'
            }
            // let param = {'currentPage': self.currentPage, 'pageSize': self.pageSize}
            self.axios({
                    method: 'patch',
                    url: self.baseurl + 'Urls/' + self.currentComponent + '/' + uid,
                    data: payLoad,

                    //params: param
                })
                .then(() => {
                    //console.log(res)

                    // 获取全部 符合当前条件的数据
                    let Params = {
                        'currentPage': self.currentPage,
                        'pageSize': self.pageSize,
                        'dateRange': encodeURIComponent(self.dateRange),
                        'UrlId': '',
                        'urlPart': self.searchItem.toLowerCase(),
                        'categoryFilter': encodeURIComponent(self.categoryChecked),
                        'statusFilter': encodeURIComponent(self.statusChecked)
                    }
                    if (data.index) {
                        self.detailIndex = data.index
                    }

                    self.fetchItems(Params)

                    // self.website = self.UrlItemData[self.detailIndex]['rootUrl']
                    // console.log(self.searchResult)
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        tagInvalid: function (data) {

            // 将url 标记为 无效
            //console.log(data)
            let self = this
            let uid = data.uid
            self.detailIndex = data.index
            let payLoad = {
                'status': '无效'
            }
            let param = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            self.axios({
                    method: 'patch',
                    url: self.baseurl + 'Urls/' + self.currentComponent + '/' + uid,

                    data: payLoad,
                    params: param
                })
                .then(() => {
                    //console.log(res)

                    // 获取全部 符合当前条件的数据
                    let Params = {
                        'currentPage': self.currentPage,
                        'pageSize': self.pageSize,
                        'dateRange': encodeURIComponent(self.dateRange),
                        'UrlId': '',
                        'urlPart': self.searchItem.toLowerCase(),
                        'categoryFilter': encodeURIComponent(self.categoryChecked),
                        'statusFilter': encodeURIComponent(self.statusChecked)
                    }
                    if (data.index) {
                        self.detailIndex = data.index
                    }

                    self.fetchItems(Params)

                    // self.website = self.UrlItemData[self.detailIndex]['rootUrl']
                    // console.log(self.searchResult)
                })
                .catch(err => {
                    //console.log(err)
                    self.$Message.error(err.response.data.detail);
                })
        },
        seeUrlDetail: function (row, index) {
            // console.log(row,index)
            // this.website = row.rootUrl
            this.detailIndex = index
            this.seeDetailKey = this.seeDetailKey + 1
            //this.changeDetailWindowShow(true)
            this.DetailWindowShow = true

        },
        // 日历相关
        TimeChange: function (daterange) {
            let self = this
            //console.log('time changed')
            self.dateRange = daterange

            //日期被重新筛选，激发重新搜索
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'UrlId': '',
                'urlPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked)
            }
            self.fetchItemsES(Params)
        },
        resetSearch: function (status) {
            if (status === false) {
                // 隐藏
                // console.log('true')
                this.searchResult = []
            }
        },
        resetInput: function () {
            let self = this
            //console.log('reset input')
            self.searchItem = ''
            self.searchResult = []

            // 以下 不应该在此处清空 赶脚
            //self.categoryChecked = []
            //self.statusChecked = []
            //self.dateRange = ['','']

            // console.log( this.searchItem, this.searchResult)
            //按照当前其他筛选情况进行 再次查询

            //url输入 被重新筛选 为空 ，激发重新搜索（完全搜索）
            self.changeSearchDisplay('')
            self.detailIndex = 0
            self.fetchAllItems()
        },

        handleFilter: function (column) {
            // 处理 分类 和 状态 筛选 ,帅选重置 的时候 也是这个 函数
            // console.log(column)
            let self = this
            let chekced = {
                'key': column['key'],
                'checked': column['_filterChecked']
            }
            if (chekced.key === 'category') {
                self.categoryChecked = chekced['checked']
            } else if (chekced.key === 'status') {
                self.statusChecked = chekced['checked']
            }
            // console.log( self.statusChecked, self.categoryChecked)

            //重新筛选，激发重新搜索  ，包含 状态 和 分类. 此时 包含的查询参数  必须有: currentPage, pageSize, 可能有: urlPart,categoryFilter ,statusFilter

            self.currentPage = 1
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'urlPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked)
            }
            self.fetchItemsES(Params)

        },
        singleSearch: function (item) {
            // search item with specifif uid ,so only one will return
            let self = this
            self.searchItem  = item[0]
            self.changeSearchDisplay(item[1])
            //console.log('singleSearch')
            //console.log('uid', item)
            self.searchResult = [] //disapper options window
            // 当进行 single search的时候，因为只关注一条记录，所以，其他筛选项是被忽略的，将他们重设为默认值。

            self.categoryChecked = []
            self.statusChecked = []
            self.dateRange = ['', '']
            // 下面进行 单条 search

            self.currentPage = 1
            // let pageParams = {'currentPage':self.currentPage,'pageSize':self.pageSize, 'UrlId': item['_id']['$oid'] }
            //let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'UrlId': item['_id']['$oid']}
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'dateRange':encodeURIComponent(self.dateRange),'UrlId': item['_id']['$oid'],'urlPart': '' ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'statusFilter': encodeURIComponent(self.statusChecked)}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'UrlId': item[0]
            }
            self.fetchItems(Params)
            //self.searchItem = '' // 恢复
        },

        batchSearch: function (part) {
            // 输入特定查询，按下回车键或 搜索按钮时 ，触发，会返回所有符合条件的项目 或为空
            let self = this
            //console.log('batchSearch')
            self.searchItem = part
            self.changeSearchDisplay(part)
            this.searchResult = []
            // 下面进行 batchSearch

            self.currentPage = 1
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'urlPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked)
            }
            // console.log(Params)
            self.fetchItemsES(Params)

        },
        urlSearch: function () {
            // console.log('urlSearch running ...')
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
                // 全部返回，所以 页面设置 为  0，0 
                let Params = {
                    'currentPage': 0,
                    'pageSize': 0,
                    'UrlId': '',
                    'dateRange': encodeURIComponent(self.dateRange),
                    'urlPart': self.searchItem.toLowerCase(),
                    'categoryFilter': encodeURIComponent(self.categoryChecked),
                    'statusFilter': encodeURIComponent(self.statusChecked)
                }
                // self.fetchItems(Params)
                self.axios({
                        method: 'get',
                        url: self.baseurl + 'Urls/' + self.currentComponent,

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
            // console.log('打开的文件: ',file.name)
            let Alldata = []
            let rootUrlStore = [] // 用来存储 唯一的 rooturl， 暂时进行整合

            // xlsx 组件解析 文件内容到 json
            let reader = new FileReader();
            reader.readAsArrayBuffer(file);

            reader.onload = function (e) {
                let data = new Uint8Array(e.target.result);
                let workbook = self.$XLSX.read(data, {
                    type: 'array'
                });
                // console.log('workbook-url',workbook.Sheets.Urls)
                // 前一行是 header，所以略过。第二行是空行，空行在读的时候已经被 略过
                let dataFormat = self.$XLSX.utils.sheet_to_json(workbook.Sheets.Urls, {
                    header: 1,
                    blankrows: false,
                    defval: '' // 空的项，读为 null
                }).slice(2)
                //console.log('dataFormat', dataFormat)
                for (let index in dataFormat) {
                    // console.log('dataFormat[index]', dataFormat[index])
                    let cunrrentIndex = rootUrlStore.indexOf(dataFormat[index][0])
                    if (cunrrentIndex !== -1) {
                        // 已经存在，直接往 Alldata 里添加
                        if (dataFormat[index][1] !== '' || dataFormat[index][2] !== '') {
                            Alldata[cunrrentIndex]['urlIncludePath'].push({
                                'path': dataFormat[index][1].trim(),
                                'type': dataFormat[index][2].trim()
                            })
                        }

                        Alldata[cunrrentIndex]['urlIncludeIndex']++
                        if (dataFormat[index][3] !== '' || dataFormat[index][4] !== '') {
                            Alldata[cunrrentIndex]['urlExcludePath'].push({
                                'path': dataFormat[index][3].trim(),
                                'type': dataFormat[index][4].trim()
                            })
                        }

                        Alldata[cunrrentIndex]['urlExcludeIndex']++
                    } else {
                        // 还未存在，先添加到  rootUrlStore，再往 Alldata里面 添加
                        let newIndex = rootUrlStore.push(dataFormat[index][0]) - 1
                        Alldata[newIndex] = {
                            'status': '未开始'
                        }
                        Alldata[newIndex]['rootUrl'] = dataFormat[index][0].trim()
                        Alldata[newIndex]['urlIncludePath'] = []
                        if (dataFormat[index][1] !== '' || dataFormat[index][2] !== '') {
                            Alldata[newIndex]['urlIncludePath'].push({
                                'path': dataFormat[index][1].trim(),
                                'type': dataFormat[index][2].trim()
                            })
                        }

                        Alldata[newIndex]['urlIncludeIndex'] = 1
                        Alldata[newIndex]['urlExcludePath'] = []
                        if (dataFormat[index][3] !== '' || dataFormat[index][4] !== '') {
                            Alldata[newIndex]['urlExcludePath'].push({
                                'path': dataFormat[index][3].trim(),
                                'type': dataFormat[index][4].trim()
                            })
                        }

                        //Alldata[newIndex]['urlExcludeIndex'] = 1
                        Alldata[newIndex]['category'] = dataFormat[index][5].trim().replace(/，/g, ',').split(',') // category是一个数组
                        // Alldata[newIndex]['status'] = '未开始' //编辑页面会添加
                    }
                }
                //console.log('Alldata', Alldata)
                // 筛选 不合规范的数据 ,badData存放有问题的数据， okData存放 没有问题的数据
                // 每次使用前 都清空
                self.badData = []
                self.okData = []
                for (let ele in Alldata) {
                    let tempRow = Alldata[ele]
                    //console.log('tempRow', tempRow)
                    if (!tempRow['rootUrl'].toLowerCase().startsWith('https://') && !tempRow['rootUrl'].toLowerCase().startsWith('http://') || tempRow['rootUrl'] === '') {
                        // 如果 rootUrl 不合法，添加到  badData，并跳出循环
                        self.badData.push(tempRow)
                        continue
                    }
                    if (tempRow['category'][0] === '') {
                        // 如果 category 为空，添加到 baddata，并跳出循环
                        //console.log('category空')
                        tempRow['category'] = [] // 重写为 []
                        self.badData.push(tempRow)
                        continue
                    } else {
                        // 对于 目录选项，首先删除 未定义的 目录，如果为空，添加异常，否则正常继续
                        let tempCategory = []
                        //console.log(tempCategory)
                        for (let ele in tempRow['category']) {
                            if (self.rowCategoies.includes(tempRow['category'][ele])) {
                                tempCategory.push(tempRow['category'][ele])
                            }
                        }

                        // 替换为 有效的分类列表
                        tempRow['category'] = tempCategory
                        if (tempCategory.length === 0) {
                            // category为空，错
                            self.badData.push(tempRow)
                            continue
                        }
                    }
                    // 循环 urlExcludePath 
                    let flags = 0
                    //console.log('tempRow[urlExcludePath]', tempRow['urlExcludePath'])
                    for (let ele2 in tempRow['urlExcludePath']) {
                        let rrowData = tempRow['urlExcludePath'][ele2]
                        //console.log('rrowData', rrowData)
                        // 如果 path 和 type 都为空，是允许的，直接跳过，检查下一个
                        if (rrowData['path'].toLowerCase() === '' && rrowData['type'].toLowerCase() === '') {
                            //rrowData = []
                            continue
                        }

                        if (!rrowData['path'].toLowerCase().startsWith('https://') && !rrowData['path'].toLowerCase().startsWith('http://') || rrowData['path'] === '') {
                            // path错误
                            flags = 1
                            break
                        }
                        if (rrowData['type'].toLowerCase() !== 'regex' && rrowData['type'].toLowerCase() !== '包含') {
                            // type 错误
                            rrowData['type'] = '' // 过滤掉非法值
                            flags = 1
                            break
                        }
                    }
                    if (flags === 1) {
                        self.badData.push(tempRow)
                        continue
                    }

                    // 循环 urlIncludePath 
                    let flags2 = 0
                    for (let ele2 in tempRow['urlIncludePath']) {
                        let rrowData = tempRow['urlIncludePath'][ele2]

                        // 如果 path 和 type 都为空，是允许的，直接跳过，检查下一个
                        if (rrowData['path'].toLowerCase() === '' && rrowData['type'].toLowerCase() === '') {
                            //rrowData = []
                            continue
                        }

                        if (!rrowData['path'].toLowerCase().startsWith('https://') && !rrowData['path'].toLowerCase().startsWith('http://') || rrowData['path'] === '') {
                            // path错误
                            flags2 = 1
                            break
                        }
                        if (rrowData['type'].toLowerCase() !== 'regex' && rrowData['type'].toLowerCase() !== '包含') {
                            // type 错误
                            rrowData['type'] = '' // 过滤掉非法值
                            flags2 = 1
                            break
                        }
                    }
                    if (flags2 === 1) {
                        self.badData.push(tempRow)
                        continue
                    }

                    // 如果以上都没有问题， 该项添加到 okData
                    self.okData.push(tempRow)
                    //console.log('good')
                }
                // console.log('okData', self.okData)
                // console.log('badData', self.badData)
                if (self.badData.length !== 0) {
                    // 如果 有错误的数据， 进入编辑界面，并显示 错误的数据；没有错误数据，直接提交到后台。
                    self.formCustom = {
                        itemIndex: self.badData.length,
                        uid: '',
                        Items: self.badData
                    }
                    self.urlItemPageTitle = '批量添加 待修正项'
                    self.xyz--
                    self.urlItemWindowShow = true
                } else {
                    // 直接上传
                    self.handleUrlNewItem({
                        'uid': '',
                        'data': []
                    }) // badData为空
                }

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
            // console.log(uids)
            self.axios({
                    method: 'delete',
                    url: self.baseurl + 'Urls/' + self.currentComponent,

                    data: uids
                })
                .then(res => {
                    // console.log(res)
                    self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.selectedItemList = []
                    self.UrlItemData = res.data.content
                })
                .catch(err => {
                    console.log(err)
                    //console.log(err.response.data.detail)
                    // self.$Message.error(err.response.data.detail);

                })

        },
        handleSelectRow: function () {
            this.selectedItemList = this.$refs.table.getSelection()
            // console.log(this.selectedItemList)

            let temp = []
            for (let ele in this.selectedItemList) {
                let lineData = this.selectedItemList[ele]
                //console.log('vvv', lineData['word'])
                if (this.selectedOldUrlsList.indexOf(lineData['url']) !== -1) {
                    //console.log('存在，跳过')
                    continue
                } else {
                    //console.log('不存在，继续')
                    temp.push({
                        'url': lineData['rootUrl'],
                        'status': lineData['status']
                    })
                }
            }
            // 将 当前页数据 插入 selectedOldFull， 要查重

            this.selectedTotal = [...new Set(this.selectedOldFull.concat(temp))]
            //console.log(self.selectedTotal, self.selectedOldFull, self.selectedOldUrlsList)
        },
        exportDataX: function () {
            let self = this

            // 当没有选项被选中时，默认选中打印当前页
            if (self.selectedItemList.length !== 0) {

                if (self.selectedItemList.length === self.UrlItemData.length) {
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
            self.pageData2Export = self.UrlItemData
            self.expordDataKey++
            self.exportWindowShow = true

        },
        Urledit: function (xrow) {
            let self = this
            // console.log(xrow)
            //
            let formCustom = {}
            formCustom.uid = xrow['_id']['$oid']
            formCustom.itemIndex = 1
            formCustom.Items = []
            formCustom.Items.push({
                'rootUrl': xrow.rootUrl
            })
            formCustom.Items[0].category = xrow.category

            // formCustom.statusEdit = xrow.status
            let urlIncludeTemp = []
            // change urlIncludePath and urlExcludePath
            for (let ele in xrow.urlIncludePath) {
                urlIncludeTemp.push(xrow.urlIncludePath[ele])
            }

            let urlExcludeTemp = []
            // change urlIncludePath and urlExcludePath
            for (let ele in xrow.urlExcludePath) {
                urlExcludeTemp.push(xrow.urlExcludePath[ele])
            }
            formCustom.Items[0].urlIncludePath = urlIncludeTemp
            formCustom.Items[0].urlExcludePath = urlExcludeTemp
            formCustom.Items[0].urlIncludeIndex = urlIncludeTemp.length
            formCustom.Items[0].urlExcludeIndex = urlExcludeTemp.length

            self.urlItemPageTitle = '单条编辑'
            self.formCustom = formCustom
            // console.log('xxxx',self.formCustom)
            //this.changeUrlItemWindowShow(true)
            self.urlItemWindowShow = true
            self.xyz--
        },
        fetchAllItems: function () {
            let self = this
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'UrlId': '',
                'urlPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked)
            }
            self.fetchItems(Params)

        },

        fetchItems: function (getParams) {
            let self = this
            let Params = getParams
            self.loading = true
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Urls/' + self.currentComponent,

                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.seeDetailKey = self.seeDetailKey + 1
                    self.UrlItemData = res.data.content
                    self.dbName = res.data.dbName
                    //console.log('self.dbName', self.dbName)
                    self.loading = false
                })
                .catch(err => {
                    self.loading = false
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        fetchItemsES: function (getParams) {
            let self = this
            let Params = getParams
            self.loading = true
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Urls/es/' + self.currentComponent,

                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.seeDetailKey = self.seeDetailKey + 1
                    self.UrlItemData = res.data.content
                    self.dbName = res.data.dbName
                    //console.log('self.dbName', self.dbName)
                    self.loading = false
                })
                .catch(err => {
                    self.loading = false
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        handleUrlDeleteItem: function (uidInfo) {
            let self = this
            let uid = uidInfo['uid']
            // 联系后台，进行删除
            self.axios({
                    method: 'delete',
                    url: self.baseurl + 'Urls/' + self.currentComponent,

                    data: [uid]
                })
                .then(res => {
                    // console.log(res)
                    self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.UrlItemData = res.data.content
                })
                .catch(err => {
                    console.log(err)
                    //console.log(err.response.data.detail)
                    // self.$Message.error(err.response.data.detail);
                })

        },
        handleUrlNewItem: function (itemInfo) {
            let self = this
            //区分 新建 还是 修改
            // 注意，新建，发送的是 对象数组(配合批量创建)，而更新只能是单个的 对象

            if (!itemInfo['uid']) {
                //页码逻辑
                self.currentPage = Math.ceil((self.itemCount + 1) / self.pageSize)
                let pageParams = {
                    'currentPage': self.currentPage,
                    'pageSize': self.pageSize
                }
                let totalData = self.okData
                if (itemInfo.data.length > 0) {
                    totalData = totalData.concat(itemInfo.data)
                }
                //console.log('totalData', totalData)
                // 新建
                // 发送到 后端

                // 只有 totalData 非空才添加
                if (totalData.length === 0) {
                    self.$Message.warning('添加项为空,跳过添加!');
                    return
                }
                self.showLoading = true
                //console.log('totalData', totalData)
                self.axios({
                        method: 'post',
                        url: self.baseurl + 'Urls/' + self.currentComponent,
                        data: totalData,
                        params: pageParams
                    })
                    .then(res => {
                        // console.log(res)
                        // self.currentPage = 1
                        if (res.data.count !== '') {
                            self.itemCount = res.data.count
                        }
                        self.UrlItemData = res.data.content
                        self.showLoading = false
                        self.$Message.success(totalData.length + '个URL上传成功');
                        //self.formCustom = self.formCustomOrigin
                    })
                    .catch(err => {
                        // console.log(err)
                        self.showLoading = false
                        //console.log(err.response.data.detail)
                        self.$Message.error({
                            content: JSON.stringify(err.response.data.detail),
                            duration: 0,
                            closable: true
                        });
                        //self.formCustom = self.formCustomOrigin
                        let Params = {
                            'currentPage': self.currentPage,
                            'pageSize': self.pageSize,
                            'dateRange': encodeURIComponent(self.dateRange),
                            'UrlId': '',
                            'urlPart': self.searchItem.toLowerCase(),
                            'categoryFilter': encodeURIComponent(self.categoryChecked),
                            'statusFilter': encodeURIComponent(self.statusChecked)
                        }
                        self.fetchItems(Params)
                    })
            } else {
                //console.log(itemInfo)
                // 修改
                let pageParams = {
                    'currentPage': self.currentPage,
                    'pageSize': self.pageSize
                }
                self.showLoading = true
                self.axios({
                        method: 'put',
                        url: self.baseurl + 'Urls/' + self.currentComponent + '/' + itemInfo.uid,
                        data: itemInfo['data'][0], //更新，只有一项

                        params: pageParams
                    })
                    .then(res => {
                        // console.log(res)
                        // self.currentPage = 1
                        if (res.data.count !== '') {
                            self.itemCount = res.data.count
                        }
                        self.showLoading = false
                        self.UrlItemData = res.data.content
                    })
                    .catch(err => {
                        // console.log(err)
                        self.showLoading = false
                        //console.log(err.response.data.detail)
                        self.$Message.error(err.response.data.detail);
                    })
            }

        },
        pageChange: function (pageIndex) {
            // console.log(pageIndex)
            let self = this
            self.currentPage = pageIndex
            self.detailIndex = 0
            self.fetchAllItems()

            // 主题词相关
            self.selectedOldFull = JSON.parse(JSON.stringify(self.selectedTotal))
            for (let ele in self.selectedOldFull) {
                let tt = self.selectedOldFull[ele]
                self.selectedOldUrlsList.push(tt.url)
            }
            //console.log(self.selectedTotal, self.selectedOldFull, self.selectedOldUrlsList)

        },
        pageSizeChange: function (pageSize) {
            let self = this
            self.pageSize = pageSize
            self.currentPage = 1

            self.detailIndex = 0
            // console.log(pageSize)
            self.fetchAllItems()

            // 主题词相关
            self.selectedOldFull = JSON.parse(JSON.stringify(self.selectedTotal))
            for (let ele in self.selectedOldFull) {
                let tt = self.selectedOldFull[ele]
                self.selectedOldUrlsList.push(tt.url)
            }
            //console.log(self.selectedTotal, self.selectedOldFull, self.selectedOldUrlsList)

        },
        addItem: function () {
            let self = this
            self.urlItemPageTitle = '手动添加'
            // this.formCustom = this.formCustomOrigin
            // console.log(this.formCustom)
            // console.log(this.formCustomOrigin)
            self.formCustom = {
                    itemIndex: 1,
                    uid: '',
                    Items: [{
                        //status: 1,
                        //index: 1,
                        rootUrl: '',
                        category: [],
                        //category: self.rowCategoies,
                        statusEdit: '未开始',
                        urlIncludeIndex: 0,
                        urlExcludeIndex: 0,
                        urlIncludePath: [],
                        urlExcludePath: []
                    }]
                },
                self.xyz--
            self.urlItemWindowShow = true
        },
        addItems: function () {
            this.urlItemPageTitle = '多条添加'
        },
        runcrawler: function (urlss) {
            //console.log('urlss', urlss)
            let self = this
            if (urlss.length === 0) {
                self.$Message.warning('未选择URL!');
            } else {
                // 获取 带 爬取 的 url列表
                let urls = []
                for (let ele in urlss) {
                    urls.push(urlss[ele]['url'])
                }

                // console.log('urls', urls)
                let configure = {
                    "id": "kms_url_crawl",
                    "version": "1.4",
                    "params": {
                        "spider_name": "minions.demo14",
                        "mongo_ip": "114.67.113.229",
                        "mongo_username": "root",
                        "mongo_password": "root",
                        "mongo_port": "8004",
                        "mongo_db": self.dbName,
                        "mongo_collection": 'Urls',
                        "query_field": "rootUrl",
                        "url_field": "rootUrl",
                        "mongo_filter": urls,
                        "mongo_save_ip": "114.67.113.229",
                        "mongo_save_username": "root",
                        "mongo_save_password": "root",
                        "mongo_save_port": "8004",
                        "mongo_save_db_name": self.dbName,
                        "mongo_save_collection_name": "Articles"
                    }
                }
                //console.log(configure, urls)
                // 发送 爬取命令
                self.axios({
                        method: 'post',
                        headers: {
                            'content-type': 'application/json'
                        },
                        url: self.crowlerAddr + 'spider/call',
                        data: configure
                    })
                    .then(res => {
                        //console.log('爬虫返回值:', res)
                        // 将 爬虫 条件，爬取的数据，时间戳，哪个用户 爬取的，以及 爬虫端返回的状态，保存到服务器端, 当前项目中的新表:  crawlerMission
                        let taskID = res.data.data.task
                        let crawlerInfo = {
                            'operator': localStorage.getItem('kwmUser'),
                            'taskID': taskID,
                            'targets': urls,
                            'status': 'unknown'
                        }
                        // 将爬取所有相关信息，保存在服务端
                        self.axios({
                                method: 'post',
                                url: self.baseurl + 'Urls/crawlerMission/' + self.currentComponent,
                                data: crawlerInfo
                            })
                            .then(() => {
                                //console.log('爬虫任务，保存在服务端成功!')
                                //5s后刷新 状态
                                //setTimeout(() => {
                                self.fetchCrawlerStatus()
                                //}, 1000)

                                //self.$Message.info('当前爬取源信息，已经保存到服务端!');
                            })
                            .catch(err => {
                                console.log(err)
                                //self.$Message.warning('当前爬取源信息，保存到服务端失败!');
                            })

                    })
                    .catch(err => {
                        console.log('爬虫返回错误值:', err)
                    })
            }

        }
    }
}
</script>

<style scoped>
.Url {
    margin: 5px;
    overflow: auto !important
}

.Url-actions {
    display: flex
}

>>>.ivu-table-cell {
    padding: 5px !important
}

.Url>>>.ivu-input-group .ivu-input {}

.Url-table {
    font-weight: 450;
    overflow: auto
}

.url-url-select-date {
    display: flex;
    align-items: center
}

.url-url-select {
    display: inline-block;
}

.url-label {
    border: 1px solid #dcdee2;
    padding: 2px 3px;
    height: 32px;
    text-align: center;
    border-radius: 4px
}

.url-select-option.url-select-option {
    min-width: 156px;
    position: absolute;
    will-change: top, left;
    transform-origin: center top;
    top: 32px;
    left: 0px;
}

.ivu-icon.ivu-icon-ios-calendar-outline {
    padding-top: 32px
}

.url-p {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 5px;
    flex-wrap: wrap
}

.url-p2 {
    margin-left: 50px;
    flex: 4;
    display: flex;
    align-items: center;
    justify-content: space-between
}

.url-p21,
.url-p22,
.url-p23,
.url-p24 {
    margin: 0 2px;
}
</style>
