<template>
<div>
    <div class="Article-button-group">
        <i-button type="error" icon="md-trash" @click="deleteConfirm">删除</i-button>
        <i-upload ref="upload" action="" :show-upload-list="false" :before-upload="handleBeforeUpload">
            <i-button type="primary" icon="md-cloud-upload" @click="addItems">批量添加</i-button>
        </i-upload>
        <i-button class="download-Template" type="primary" @click="downloadTemplate" icon="md-copy">下载模板</i-button>

        <i-button v-if="digStatus === 'finished' || digStatus === ''" height="200" style="color: #fff;background-color: #057009" onMouseOver="this.style.color='#b6f204'" onMouseOut="this.style.color='#fff'" icon="md-power" @click="runDig">开始挖词</i-button>
        <i-button v-else type="primary" :disabled="true">正在挖词...</i-button>
    </div>
    <i-page :total="itemCount" :current="currentPage" placement="bottom" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />
    <i-table class="Article-table" :columns="columns1" :data="ArticleItemData" :loading="loading" @on-selection-change="handleSelectRow()" ref="table" stripe border @on-filter-change="handleFilter">
        <template slot-scope="{ row,index }" slot="action">
            <div>
                <i-button type="primary" size="small" style="margin-right: 5px" @click="seeArticleDetail(row,index)">检视</i-button>
            </div>
        </template>
    </i-table>
    <i-page :total="itemCount" :current="currentPage" placement="top" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />

    <!--弹出框都在此地-->
    <i-seeUrlConfig :url2Sees="url2See" :showSeeUrlConfig.sync="showSeeUrlConfig" :key="seeUrlConfigKey"></i-seeUrlConfig>
    <i-seeDetails :rawCategories="rawCategories" :pageSize="pageSize" :currentPage="currentPage" :currentIndex.sync="currentIndex" :showSeeDetail.sync="showSeeDetail" :key="seeDetailKey" @force-refresh="forceRefresh"></i-seeDetails>
    <i-digWordsWarn :UserDictItemCount="UserDictItemCount" :StopDictItemCount="StopDictItemCount" :showdigWords.sync="showdigWords" @runDig="realRunDig"></i-digWordsWarn>
    <i-articleUpload :rowCategoies="rawCategories" :ArticleWindowShow.sync="ArticleWindowShow" :key="xyz" :Alldata="Alldata" @uploadArticlesnewItem="uploadArticlesnewItem"></i-articleUpload>

</div>
</template>

<script>
import {
    mapState,
    mapMutations
} from 'vuex'
import seeUrlConfig from '@/components/Articles/seeUrlConfig.vue'
import seeDetails from '@/components/Articles/seeDetails.vue'
import digWordsWarn from '@/components/Articles/digWordsWarn.vue'
import articleUpload from '@/components/Articles/articleUpload.vue'
import urlSearch from '@/components/Articles/urlSearch.vue'

export default {
    name: 'Articles',
    data() {
        var global = this // 如果不这样， render 中找不到 正确的 this
        return {
            dbName: '', // 当前项目 所在的  mongo 数据库 名称
            digStatus: '',
            Alldata: {},
            formCustom: [],
            ArticleWindowShow: false,
            xyz: 2000,
            excelNoteData: [
                ['', '使用前必看！'],
                ['', ''],
                [1, '请将数据按照示例格式填写在Articles sheet中'],
                [2, '不要修改Articles sheet的名称，否则会出错'],
                [3, '不要使用中文逗号等分隔符'],
                [4, '从第3行开始写'],
                [5, '当前可选的目录。填写的未在可选目录中的目录,会被忽略掉，此处小心'],
                []
            ],
            excelTemplateData: {
                data: [
                    ["title", "keywords", "desciption", "rawContent", "body", "分类"],
                    ["", "", "", "", "", ""],
                    ["店宝宝", "创业,电商,自由,财富", "这是一个帮助中小用户淘宝开店的产品解决方案", "免费帮你开店", "世界很美好啊,但是到处都有战争，不要战争，要和平！", ""],
                    ["完美邮箱", "完美,88,个人,企业,方便,祝福", "为个人用户提供邮箱服务，同时也为企业用户提供服务", "简单快捷开通邮箱，安全性好", "还在翻墙用谷歌邮箱吗？还在用满是广告的网易邮箱吗？还在用丑陋不堪的腾讯邮箱吗？来试试完美邮箱吧！", ""]
                ]
            },
            rawCategories: [],
            UserDictItemCount: '',
            StopDictItemCount: '',
            // articleDetail: [],
            currentIndex: 0,
            searchItem: '',
            stopDictEmpty: false,
            userDictEmpty: false,
            showSeeUrlConfig: false,
            showdigWords: false,
            showSeeDetail: false,
            seeUrlConfigKey: 0,
            seeDetailKey: 10000,
            url2See: '',
            currentPage: 1,
            pageSize: 10,
            loading: false,
            itemCount: 0,
            dateRange: ['', ''],
            ArticleItemData: [],
            projetcCategoriesList: [],
            selectedItemList: [],
            categoryChecked: [],
            urlChecked: [],
            statusChecked: [],
            lengthChecked: [],
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
                    title: '来源',
                    key: 'root',
                    align: 'left',
                    minWidth: 100,
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params)
                        if (params.row.root) {
                            if (params.row.root.toLowerCase().startsWith("http://") || params.row.root.toLowerCase().startsWith("https://")) {
                                return h('a', {
                                    on: {
                                        click: () => {
                                            // window.open(params.row.url)
                                            // 激活 seeUrlConfig
                                            // console.log(params.row.root)
                                            this.handleSeeUrlConfig(params.row.root)
                                            // this.seeUrlConfigKey = this.seeUrlConfigKey +1
                                            // this.showSeeUrlConfig = true
                                        }
                                    }
                                }, params.row.root)
                            } else {
                                return (h('p', params.row.root))
                            }
                        }
                    },
                    fixed: 'left'
                },
                {
                    title: 'url',
                    key: 'url',
                    align: 'left',
                    minWidth: 100,
                    //filters: [{
                    //    'label': '有效',
                    //    'value': '1'
                    //}, {
                    //    'label': '无效',
                    //    'value': '2'
                    //}],
                    //filterMethod(value, row) {
                    //    // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                    //    return row //什么都不做，由专门的函数进行后端筛选
                    //},
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params)
                        if (params.row.url !== 0) {
                            if (params.row.url.endsWith('.csv') || params.row.url.endsWith('.txt') || params.row.url.endsWith('.json') || params.row.url.endsWith('.xlsx') || params.row.url.endsWith('.xls')) {
                                return h('p', params.row.url)
                            } else {
                                return h('a', {
                                    on: {
                                        click: () => {
                                            window.open(params.row.url)
                                        }
                                    }
                                }, params.row.url)
                            }
                        }
                    },
                    fixed: 'left',
                    renderHeader(h) {
                        return h('span', [
                            h('span', 'url'),
                            h('i-poptip', {
                                    props: {
                                        title: "url过滤",
                                        content: "content",
                                        placement: "right-start",
                                        transfer: true,
                                        trigger: 'click',
                                        closable: true,
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
                    title: 'title',
                    key: 'title',
                    align: 'center',
                    minWidth: 150,
                    resizable: true,
                },
                {
                    title: 'keywords',
                    key: 'keywords',
                    align: 'center',
                    minWidth: 90,
                    resizable: true,
                    render: (h, params) => {
                        if (params.row.keywords) {
                            // console.log(params.row)
                            // return (h('p', params.row.keywords.join(';')))
                            return (h('p', params.row.keywords))
                        }
                    }
                },
                {
                    title: 'desciption',
                    key: 'description',
                    align: 'center',
                    minWidth: 100,
                    resizable: true,
                },
                {
                    title: 'rawContent',
                    key: 'rawContent',
                    align: 'center',
                    width: 90,
                    resizable: true,
                },
                {
                    title: 'body',
                    key: 'body',
                    align: 'center',
                    //ellipsis: true,
                    tooltip: true,
                    minWidth: 350,
                    resizable: true,
                    render: (h, params) => {
                        return h('p', {
                            style: {
                                color: '#057009',
                                'font-weight': 400,
                                'overflow': 'auto',
                                'max-height': '150px'
                            },
                        }, params.row.body)
                    }

                },
                {
                    title: '长度',
                    key: 'Length',
                    align: 'center',
                    minWidth: 60,
                    resizable: true,
                    // filters 对应项目:
                    // 1 -> [0,50], 2 -> [50,100], 3 -> [100,300], 4 -> [300,500],5 -> [500,1000], 6 -> [1000,10000]
                    filters: [{
                        'label': '0-50',
                        'value': '1'
                    }, {
                        'label': '50-100',
                        'value': '2'
                    }, {
                        'label': '100-300',
                        'value': '3'
                    }, {
                        'label': '300-500',
                        'value': '4'
                    }, {
                        'label': '500-1000',
                        'value': '5'
                    }, {
                        'label': '1000-10000',
                        'value': '6'
                    }],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        return row //什么都不做，由专门的函数进行后端筛选
                    },
                    render: (h, params) => {
                        if (params.row.Length) {
                            // console.log(params.row)
                            return (h('p', params.row.Length)) //.length))
                        }
                    }
                },
                {
                    title: '分词',
                    key: 'splitWords',
                    align: 'center',
                    minWidth: 350,
                    resizable: true,
                    render: (h, params) => {
                        if (params.row.splitWords) {
                            // console.log(params.row)
                            return (h('p', {
                                style: {
                                    'color': '#212891',
                                    'font-weight': '400',
                                    'overflow': 'auto',
                                    'text-align': 'left',
                                    'max-height': '150px'
                                }
                            }, params.row.splitWords.join(' ; ')))
                        }
                    }
                },
                {
                    title: '分类',
                    key: 'category',
                    align: 'center',
                    minWidth: 90,
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
                    resizable: true,
                    filters: [{
                        'label': '无效',
                        'value': '无效'
                    }, {
                        'label': '已添加',
                        'value': '已添加'
                    }, {
                        'label': '已分词',
                        'value': '已分词'
                    }, {
                        'label': '挖词中',
                        'value': '挖词中'
                    }, {
                        'label': '已挖词',
                        'value': '已挖词'
                    }],
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
                                    'background-color': 'rgba(100, 108, 122, 0.5)',
                                }
                            }, params.row.status)
                        } else if (params.row.status === '已添加') {
                            return h('p', params.row.status)
                        } else if (params.row.status === '已分词') {
                            return h('p', {
                                style: {
                                    'background-color': 'rgba(151, 221, 144, 0.5)',
                                }
                            }, params.row.status)
                        } else if (params.row.status === '已挖词') {
                            return h('p', {
                                style: {
                                    'background-color': 'rgba(7, 249, 23, 0.5)',
                                }
                            }, params.row.status)
                        }

                    }
                },
                {
                    title: '变更时间',
                    key: 'modifiedTime',
                    align: 'center',
                    minWidth: 90,
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
                    minWidth: 60,
                    resizable: true,
                    fixed: 'right'
                }
            ],
        }
    },
    computed: {
        ...mapState(['baseurl', 'currentComponent','crowlerAddr']),
    },
    components: {
        'i-seeUrlConfig': seeUrlConfig,
        'i-seeDetails': seeDetails,
        'i-digWordsWarn': digWordsWarn,
        'i-articleUpload': articleUpload
    },
    mounted() {
        let Params = {
            'currentPage': self.currentPage,
            'pageSize': self.pageSize
        }
        // this.loading = true
        this.fetchItems(Params)
        this.fetchProjectCategories()
        this.fetchDigStatus()
    },
    methods: {
        ...mapMutations(['changeSearchDisplay']),
        fetchDigStatus: function () {
            let self = this
            // 服务端获取 最近一次任务 id 及 状态
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Articles/digMission/' + self.currentComponent,
                })
                .then(res => {
                    // console.log(res)
                    if (res.data.content.length > 0) {
                        let taskID = res.data.content[0].taskID
                        self.digStatus = res.data.content[0].status
                        // console.log('self.digStatus', self.digStatus)
                        // 如果状态时 未完成，则 获取最新状态，否则，不获取
                        if (self.digStatus === 'unknown') {
                            // 获取状态
                            //console.log('去挖词服务端获取最新状态...')
                            self.axios({
                                    method: 'get',
                                    url: self.crowlerAddr + 'spider/status/' + taskID,
                                })
                                .then(res => {
                                    //console.log('挖词服务端最新状态' + JSON.stringify(res.data))
                                    if (res.data.status === 'success') {
                                        self.digStatus = res.data.data.status
                                        //console.log(this.digStatus, taskID)
                                        // 如果已完成，将状态 同步到 服务端  digMission
                                        if (self.digStatus === 'finished') {
                                            // 更新 dig mission 状态
                                            self.axios({
                                                    method: 'patch',
                                                    url: self.baseurl + 'Articles/digMission/' + self.currentComponent + '/' + taskID,
                                                    params: {
                                                        'status': 'finished'
                                                    }
                                                })
                                                .then(() => {
                                                    //console.log('挖词任务完成状态，更新到服务端成功!')

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
        realRunDig: function () {
            // 真正开始挖词
            let self = this

            if (self.selectedItemList.length === 0) {
                self.$Message.warning('未选择语料!');
            } else {
                // 获取待 爬取的 语料uid 列表
                let uids = []
                for (let element in self.selectedItemList) {
                    uids.push(self.selectedItemList[element]['_id']['$oid'])
                }

                // console.log('urls', urls)
                let configure = {
                    "spider_name": "minions.demo14",
                    "id": "kms_waci",
                    "version": "1.0",
                    "params": {
                        "mongo_path": "mongodb://root:root@114.67.113.229:8004",
                        // "mongo_username": "root",
                        // "mongo_password": "root",
                        // "mongo_port": "8004",
                        "mongo_db": self.dbName,
                        "redis_addr": "114.67.113.171",
                        "redis_password": "redisGoodToKICK",
                        // "mongo_collection": 'Urls',
                        //"query_field": "rootUrl",
                        // "url_field": "rootUrl",
                        "mongo_filter": uids.join(','),
                        //"mongo_save_ip": "114.67.113.229",
                        //"mongo_save_username": "root",
                        //"mongo_save_password": "root",
                        //"mongo_save_port": "8004",
                        //"mongo_save_db_name": self.dbName,
                        //"mongo_save_collection_name": "Articles"
                    }
                }
                //console.log(configure, uids)
                // 发送  挖词 命令
                self.axios({
                        method: 'post',
                        headers: {
                            'content-type': 'application/json'
                        },
                        url: self.crowlerAddr + 'spider/call',
                        data: configure
                    })
                    .then(res => {
                        //console.log(res)
                        //console.log('挖词返回值:', res)
                        // 将 挖词 条件，挖取的数据，时间戳，哪个用户 挖取的，以及 挖词端返回的状态，保存到服务器端, 当前项目中的新表:  digMission
                        // 保存在服务端，同时也保存在 localstrooage中
                        let taskID = res.data.data.task

                        let digInfo = {
                            'operator': localStorage.getItem('kwmUser'),
                            'taskID': taskID,
                            'targets': uids,
                            'status': 'unknown'
                        }
                        // 将 挖词 所有相关信息，保存在服务端
                        self.axios({
                                method: 'post',
                                url: self.baseurl + 'Articles/digMission/' + self.currentComponent,
                                data: digInfo
                            })
                            .then(() => {
                                //console.log('挖词任务，保存在服务端成功!')
                                //5s后刷新 状态
                                //setTimeout(() => {
                                self.fetchDigStatus()
                                //}, 5000)

                                //self.$Message.info('当前挖词源信息，已经保存到服务端!');
                            })
                            .catch(err => {
                                console.log(err)
                                //self.$Message.warning('当前挖词源信息，保存到服务端失败!');
                            })
                    })
                    .catch(err => {
                        console.log(err)
                    })
            }
        },
        resetInput: function () {
            let self = this
            //console.log('reset input')
            self.searchItem = ''
            self.searchResult = []
            self.changeSearchDisplay('')
            // console.log( this.searchItem, this.searchResult)
            //按照当前其他筛选情况进行 再次查询

            //url输入 被重新筛选 为空 ，激发重新搜索（完全搜索）
            let Params = {
                'currentPage': 1,
                'pageSize': self.pageSize
            }
            self.fetchItems(Params)
        },
        batchSearch: function (part) {
            // 输入特定查询，按下回车键或 搜索按钮时 ，触发，会返回所有符合条件的项目 或为空
            let self = this
            //console.log('batchSearch')
            self.searchItem = part
            this.searchResult = []
            self.changeSearchDisplay(part)
            // 下面进行 batchSearch
            self.currentPage = 1
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'dateRange':encodeURIComponent(self.dateRange),'wordPart':self.searchItem.toLowerCase() ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'statusFilter': encodeURIComponent(self.statusChecked)}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                //'basicWordItemId': '',
                'dateRange': encodeURIComponent(self.dateRange),
                'urlPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'lengthFilter': encodeURIComponent(self.lengthChecked),
                'weightFilter': encodeURIComponent(self.weightChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }
            // console.log(Params)
            self.fetchItemsES(Params)

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

            // self.categoryChecked = []
            // self.statusChecked = []
            // self.lengthChecked = []
            // self.weightChecked = []
            // self.dateRange = ['','']
            // 下面进行 单条 search

            self.currentPage = 1
            let Params = {
                'currentPage': 1,
                'pageSize': self.pageSize,
                'urlId': uid[0]
            }
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'UrlId': item['_id']['$oid']}
            self.fetchItems(Params)
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
            this.$XLSX.utils.book_append_sheet(new_workbook, worksheet2, "Articles")
            this.$XLSX.writeFile(new_workbook, 'Articles-template.xlsx')
        },
        forceRefresh: function (cpage) {
            //console.log('refresh page ...')
            this.currentPage = cpage
            let Params = {
                'currentPage': this.currentPage,
                'pageSize': this.pageSize,
                // 'urlPart': self.searchItem.toLowerCase(),
            }
            // this.loading = true
            this.fetchItems(Params)
        },
        // 挖词
        runDig: function () {
            let self = this
            // 挖词，先判断 用户词典 或停用词典 是否为空
            // 用户词典

            self.axios({
                    method: 'get',
                    url: self.baseurl + 'UserDict/' + self.currentComponent + '/isEmpty',
                })
                .then(res => {
                    // console.log(res)
                    self.UserDictItemCount = res.data

                    // 停用词典
                    self.axios({
                            method: 'get',
                            url: self.baseurl + 'StopDict/isEmpty',
                        })
                        .then(res => {
                            // console.log(res)
                            self.StopDictItemCount = res.data
                            //console.log(self.StopDictItemCount)
                            //console.log(self.UserDictItemCount)
                            if (self.StopDictItemCount === 0 || self.UserDictItemCount === 0) {
                                // 显示提示
                                // console.log('显示提示')
                                self.showdigWords = true
                            } else {
                                //console.log('直接进行挖词')
                                self.realRunDig()
                            }
                        })
                        .catch(err => {
                            console.log(err)
                        })
                })
                .catch(err => {
                    console.log(err)
                })
        },
        handleSeeUrlConfig: function (url) {
            // console.log(url)
            let self = this
            self.url2See = url
            self.seeUrlConfigKey = self.seeUrlConfigKey + 1
            self.showSeeUrlConfig = true
        },
        pageChange: function (pageIndex) {
            // console.log(pageIndex)
            let self = this
            self.currentPage = pageIndex
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'urlPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'lengthFilter': encodeURIComponent(self.lengthChecked)
            }
            self.fetchItemsES(Params)
        },
        pageSizeChange: function (pageSize) {
            let self = this
            self.pageSize = pageSize
            self.currentPage = 1
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'urlPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'lengthFilter': encodeURIComponent(self.lengthChecked)
            }
            self.fetchItemsES(Params)
        },
        handleSelectRow: function () {
            this.selectedItemList = this.$refs.table.getSelection()
        },
        fetchProjectCategories: function () {
            // 获取所有 该项目下的所有 目录列表
            let self = this
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Categories/' + self.currentComponent
                })
                .then(res => {
                    for (let ele in res.data.content) {
                        self.projetcCategoriesList.push({
                            'label': res.data.content[ele].categoryName,
                            'value': res.data.content[ele].categoryName
                        })
                        self.rawCategories.push(res.data.content[ele].categoryName)
                    }
                    // console.log('projetcCategoriesList',self.projetcCategoriesList)

                    // 将 excel 模板中得到 分类，全部 默认设为 当前项目所有分类
                    for (let i = 2; i <= 3; i++) {
                        self.excelTemplateData.data[i][5] = self.rawCategories.join(',')
                    }

                    self.columns1[11].filters = self.projetcCategoriesList // 必须要设置一下 ，目录列表
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        seeArticleDetail: function (row, index) {
            let self = this
            // console.log('see articles', row,index)
            // 计算需要的数据
            // let articleDetail = []
            // for (let ele in self.ArticleItemData){
            //   let body = self.ArticleItemData[ele].body
            //   let uid =  self.ArticleItemData[ele]['_id']['$oid']
            //   let split = self.ArticleItemData[ele].splitWords
            //   articleDetail.push({'body': body, 'uid': uid,'split':split})
            // }
            if (row.body) {
                // 只有存在body，才进入
                self.currentIndex = index
                // self.articleDetail = articleDetail
                self.showSeeDetail = true
                self.seeDetailKey = self - 1
            } else {
                self.$Message.warning('不存在body信息,请检查!')
            }
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
                    url: self.baseurl + 'Articles/' + self.currentComponent,

                    data: uids
                })
                .then(res => {
                    // console.log(res)
                    self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.selectedItemList = []
                    self.ArticleItemData = res.data.content
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        addItems: function () {
            console.log('addItems')
        },
        // 日历相关
        TimeChange: function (daterange) {
            let self = this
            //console.log('time changed')
            // console.log(daterange)
            self.dateRange = daterange

            //日期被重新筛选，激发重新搜索
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'dateRange':encodeURIComponent(self.dateRange),'UrlId': '','urlPart':self.searchItem.toLowerCase() ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'statusFilter': encodeURIComponent(self.statusChecked)}
            let Params = {
                'currentPage': self.currentPage,
                'urlFilter': encodeURIComponent(self.urlChecked),
                'pageSize': self.pageSize,
                'lengthFilter': encodeURIComponent(self.lengthChecked),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'dateRange': encodeURIComponent(self.dateRange)
            }
            self.fetchItemsES(Params)
        },
        handleFilter: function (column) {
            // 处理 分类 和 状态 筛选 ,筛选 重置 的时候 也是这个 函数
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
            } else if (chekced.key === 'url') {
                self.urlChecked = chekced['checked']
            } else if (chekced.key === 'Length') {
                self.lengthChecked = chekced['checked']
            }
            // console.log( self.statusChecked, self.categoryChecked)

            //重新筛选，激发重新搜索  ，包含 状态 和 分类. 此时 包含的查询参数  必须有: currentPage, pageSize, 可能有: urlPart,categoryFilter ,statusFilter
            // console.log(self.lengthChecked, self.statusChecked, self.categoryChecked)
            self.currentPage = 1
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'urlFilter': encodeURIComponent(self.urlChecked),
                'urlPart': self.searchItem.toLowerCase(),
                'lengthFilter': encodeURIComponent(self.lengthChecked),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'dateRange': encodeURIComponent(self.dateRange)
            }
            self.fetchItemsES(Params)

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
                let dataFormat = self.$XLSX.utils.sheet_to_json(workbook.Sheets.Articles, {
                    header: 1,
                    blankrows: false
                }).slice(2)
                //console.log('dataFormat',dataFormat)
                for (let index in dataFormat) {
                    let temp = {}
                    temp.root = file.name
                    temp.url = file.name.split('.')[0] + '-' + (new Date()).valueOf() + String(parseInt(Math.random() * (100000 + 1))) + '.' + file.name.split('.')[1] // 这个地方，在小概率情况下会有bug，有可能会碰撞
                    temp.title = dataFormat[index][0].trim()
                    temp.keywords = dataFormat[index][1].trim().replace(/，/g, ',').split(',') // keywords 是一个数组
                    temp.desciption = dataFormat[index][2].trim()
                    temp.rawContent = dataFormat[index][3].trim()
                    temp.body = dataFormat[index][4].trim()
                    temp.category = dataFormat[index][5].trim().replace(/，/g, ',').split(',') // category 是一个数组
                    // temp.status = '已添加'  // 后端添加
                    // Alldata[newIndex]['status'] = '未开始' //编辑页面会添加
                    Alldata.push(temp)

                }
                //console.log('Alldata', Alldata)
                //如果数据不为空， 则直接提交，否则，弹窗提示数据为空
                if (Alldata.length > 0) {
                    //self.Alldata = {
                    //    'data': Alldata
                    //}
                    self.uploadArticlesnewItem(Alldata)

                    //self.xyz--
                    //self.ArticleWindowShow = true
                } else {
                    self.$Message.info('文件中未包含有效数据!');
                }

            }
            return false // 返回false 代表 不上传
        },
        uploadArticlesnewItem: function (data) {
            let self = this
            // console.log('vvv', data)
            self.axios({
                    method: 'post',
                    url: self.baseurl + 'Articles/' + self.currentComponent,
                    data: data
                })
                .then(res => {
                    // console.log(res)
                    self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.ArticleItemData = res.data.content
                    //self.formCustom = self.formCustomOrigin
                })
                .catch(err => {
                    console.log(err)
                })
        },
        fetchItems: function (getParams) {
            let self = this
            let Params = getParams
            self.loading = true
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Articles/' + self.currentComponent,

                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1

                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.ArticleItemData = res.data.content
                    self.dbName = res.data.dbName
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
                    url: self.baseurl + 'Articles/es/' + self.currentComponent,

                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1

                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.ArticleItemData = res.data.content
                    self.dbName = res.data.dbName
                    self.loading = false
                })
                .catch(err => {
                    self.loading = false
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        }
    },

}
</script>

<style scoped>
>>>.ivu-table th {}

>>>.ivu-table-cell {
    padding: 5px !important
}

.Article-button-group {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 5px
}

>>>.Article-table tbody {
    font-weight: 450
}

.download-Template {
    margin-left: 20px
}
</style>
