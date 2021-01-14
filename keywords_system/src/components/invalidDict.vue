<template>
<div class="my-container">
    <div class="my-title">

        <i-button class="back" type="error" icon="md-refresh" @click="backToKeyWord">恢复</i-button>
        <i-button type="warning" @click="exportDataX()" icon="md-download">导出数据</i-button>
        <i-button type="primary" icon="md-add" @click="addItem()">在线添加</i-button>
        <i-button type="primary" @click="downloadTemplate" icon="md-copy">下载模板</i-button>
        <i-upload class="Url-batchUpload-button" ref="upload" action :show-upload-list="false" :before-upload="handleBeforeUpload">
            <i-button class="Url-part114 Url-newItems-button" type="primary" icon="md-cloud-upload" @click="addInvalidDictItems">批量添加</i-button>
        </i-upload>
    </div>
    <div>
        <i-page :total="itemCount" :current="currentPage" placement="bottom" :page-size="pageSize" :page-size-opts="[10,20,30,40,50,100]" size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />
    </div>

    <!--弹出框都在此地-->
    <i-invalidDictItemPage :key="refreshFlag" :formCustom2="JSON.parse(JSON.stringify(formCustom))" :invalidDictItemShow.sync="invalidDictItemShow" @createInvalidWords="createInvalidWords" @deleteInvalidWordItem="handledeleteInvalidWordItem" @UpdateInvalidWords="handleUpdateInvalidWordItem"></i-invalidDictItemPage>
    <i-exportData :key="expordDataKey" :pageSize="pageSize" :selectedFlag="selectedFlag" :selected1="selected1" :pageData2Export="pageData2Export" :exportWindowShow.sync="exportWindowShow"></i-exportData>

    <i-table class="invalid-table" :columns="columns1" :data="InvalidDictItemData" :loading="loading" @on-filter-change="handleFilter" @on-selection-change="handleSelectRow()" ref="table" stripe border>
        <template slot-scope="{ row,index }" slot="action">
            <div class="Url-actions">
                <i-button type="success" size="small" style="margin-right: 5px" @click="editInvalidDictItem(row,index)">修改</i-button>
            </div>
        </template>
    </i-table>
    <i-page :total="itemCount" :current="currentPage" placement="top" :page-size="pageSize" :page-size-opts="[10,20,30,40,50,100]" size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />
</div>
</template>

<script>
import exportData from '@/components/invalidDict/exportData.vue'
import invalidDictItemPage from '@/components/invalidDict/invalidDictItemPage.vue'
import invalidWordSearch from '@/components/invalidDict/invalidWordSearch.vue'

import {
    mapState,
    mapMutations
} from "vuex";
export default {
    name: 'invalidDict',
    data() {
        var global = this // 如果不这样， render 中找不到 正确的 this
        return {
            dateRange: ['', ''],
            sourceChecked: [],
            exportWindowShow: false,
            pageData2Export: [],
            selected1: '当前选中',
            expordDataKey: 20,
            selectedFlag: [],
            invalidDictItemShow: false,
            refreshFlag: 1000,
            excelNoteData: [
                ['', '使用前必看！'],
                ['', ''],
                [1, '请将数据按照示例格式填写在 invalidDict sheet中'],
                [2, '不要修改invalidDict sheet的名称，否则会出错'],
                [3, '每行填写一个词'],
                [4, '从第3行开始写']
            ],
            excelTemplateData: {
                data: [
                    ["无效词"],
                    [""],
                    ["毁灭"],
                    ["宇宙"]
                ]
            },
            newItemModalShow: false,
            modifyItemModalShow: false,
            currentWord: "",
            currentItem: undefined,
            searchWord: '',
            userList: [],
            operatorChecked: '',
            searchReaultListvisible: true,
            searchItem: "",
            website: "https://www.stockhey.com",
            detailIndex: 1,
            searchResult: [],
            selectedItemList: [],
            loading: false,
            itemCount: 0,
            currentPage: 1,
            pageSize: 10,
            select3: "Url",
            urlItemPageShow: false,
            urlItemPageTitle: "单条添加",
            columns1: [{
                    type: "selection",
                    align: "center",
                    width: 30,
                    resizable: true,
                    fixed: "left",
                },
                {
                    title: 'id',
                    key: 'id',
                    width: 50,
                    align: 'center',
                    //sortable: true,
                    resizable: true,
                    fixed: 'left'
                },
                {
                    title: "无效词",
                    key: "word",
                    align: "center",
                    sortable: false,
                    resizable: true,
                    renderHeader(h) {
                        return h('span', [
                            h('span', '无效词'),
                            h('i-poptip', {
                                    props: {
                                        title: "无效词全文搜索",
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
                                    h(invalidWordSearch, {
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
                    title: "时间",
                    key: "modifiedTime",
                    align: "left",
                    resizable: true,
                    renderHeader(h) {
                        return h('span', [
                            h('span', '生成时间'),
                            h('i-poptip', {
                                    props: {
                                        title: "日期过滤",
                                        content: "content",
                                        placement: "right-start",
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
                    title: "操作人",
                    key: "operator",
                    align: "left",
                    filters: [{
                        'label': '无效',
                        'value': '无效'
                    }, {
                        'label': '未开始',
                        'value': '未开始'
                    }, ],
                    filterMethod(value) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        //if (row.status === value){
                        return value //什么都不做，由专门的函数进行后端筛选
                        //}
                    },
                    resizable: true,
                },
                {
                    title: "前状态",
                    key: "exStatus",
                    align: "center",
                    resizable: true,
                },
                {
                    title: "来源",
                    key: "source",
                    align: "center",
                    minWidth: 100,
                    filters: [{
                            'label': '手动添加',
                            'value': '手动添加'
                        }, {
                            'label': '语料分词',
                            'value': '语料分词'
                        },
                        {
                            'label': '基础词',
                            'value': '基础词'
                        },
                        {
                            'label': '拓展词',
                            'value': '拓展词'
                        },
                        {
                            'label': '停止词',
                            'value': '停止词'
                        },
                        {
                            'label': '用户词',
                            'value': '用户词'
                        }
                    ],
                    filterMethod(value) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        //if (row.status === value){
                        return value //什么都不做，由专门的函数进行后端筛选
                        //}
                    },
                    resizable: true,
                },
                {
                    title: "操作",
                    key: "action",
                    width: 100,
                    slot: "action",
                    align: "center",
                    resizable: true,
                },
            ],
            InvalidDictItemData: [],
            formCustom: {},
        };
    },
    computed: {
        ...mapState([
            "baseurl",
            "currentComponent"
        ]),
    },
    mounted() {
        this.getUserInformation()
    },
    created() {
        this.fetchItems(); // 获取当前
    },
    components: {
        'i-exportData': exportData,
        'i-invalidDictItemPage': invalidDictItemPage
    },
    methods: {
        ...mapMutations(['changeSearchDisplay']),
        batchSearch: function (part) {
            // 输入特定查询，按下回车键或 搜索按钮时 ，触发，会返回所有符合条件的项目 或为空
            let self = this
            //console.log('batchSearch')
            self.searchItem = part
            self.searchResult = []
            self.changeSearchDisplay(part)
            // 下面进行 batchSearch
            self.currentPage = 1
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'dateRange':encodeURIComponent(self.dateRange),'wordPart':self.searchItem.toLowerCase() ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'statusFilter': encodeURIComponent(self.statusChecked)}
            let params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'operatorFilter': encodeURIComponent(self.operatorChecked),
                'sourceFilter': encodeURIComponent(self.sourceChecked),
                'searchItem': self.searchItem.toLowerCase(),

            }

            // console.log(Params)
            self.fetchItemsES(params)

        },
        resetInput: function () {
            let self = this
            //console.log('reset input')
            self.searchItem = ''
            self.searchResult = []
            self.changeSearchDisplay('')
            self.currentPage = 1
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            self.fetchItems(Params)
        },
        singleSearch: function (uid) {
            // search item with specifif uid ,so only one will return
            let self = this
            // console.log('singleSearch')
            // self.searchItem = ''
            //console.log('uid', uid)
            self.changeSearchDisplay(uid[1])
            self.searchResult = [] //disapper options window
            // 当进行 single search的时候，因为只关注一条记录，所以，其他筛选项是被忽略的，不发送它们

            self.currentPage = 1
            let params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'searchItemID': uid[0]
            }
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'UrlId': item['_id']['$oid']}
            self.fetchItems(params)
        },
        handleUpdateInvalidWordItem: function (newData) {
            let self = this
            //console.log('newData', newData)
            let pageParams = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            self.axios({
                    method: "patch",
                    url: self.baseurl + 'InvalidDict/' + self.currentComponent + '/' + newData.uid,
                    data: newData.data,
                    params: pageParams
                })
                .then((res) => {
                    if (res.data == 'item exist') {
                        self.$Message.info("该停止词已存在!");
                    } else {
                        if (res.data.count !== "") {
                            self.itemCount = res.data.count;
                        }
                        self.InvalidDictItemData = res.data.content;
                        self.$Message.success("修改成功!");
                    }
                })
                .catch((err) => {
                    console.log(err);
                    //self.$Message.error("修改失败!");
                    self.$Message.error({
                        content: JSON.stringify(err.response.data.detail),
                        duration: 0,
                        closable: true
                    });
                });
        },
        handledeleteInvalidWordItem: function (word) {
            let self = this
            let items = [word.word]
            // console.log(uids)
            let pageParams = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            //console.log('items', items)
            self.axios({
                    method: "delete",
                    url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                    data: items,
                    params: pageParams
                })
                .then((res) => {
                    // console.log(res)
                    self.currentPage = 1;
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    self.InvalidDictItemData = res.data.content;
                    self.$Message.success("删除成功!");
                })
                .catch((err) => {
                    console.log(err);
                    self.$Message.error("删除失败");
                });
        },
        createInvalidWords: function (DATA) {
            let self = this;
            // console.log(DATA)
            self.currentPage = Math.ceil((self.itemCount + 1) / self.pageSize)
            let pageParams = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            self.axios({
                    method: "post",
                    url: self.baseurl + "InvalidDict/" + self.currentComponent,
                    data: DATA,
                    params: pageParams
                })
                .then((res) => {
                    //console.log(res)
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    self.InvalidDictItemData = res.data.content;
                    self.$Message.success("新增成功!");

                })
                .catch((err) => {
                    console.log(err);
                    //self.$Message.error("新增失败!");
                    self.$Message.error({
                        content: JSON.stringify(err.response.data.detail),
                        duration: 0,
                        closable: true
                    });
                });

        },
        addInvalidDictItems: function () {},
        downloadTemplate: function () {
            let worksheet1 = this.$XLSX.utils.aoa_to_sheet(this.excelNoteData)
            let worksheet2 = this.$XLSX.utils.aoa_to_sheet(this.excelTemplateData.data)
            let new_workbook = this.$XLSX.utils.book_new()
            this.$XLSX.utils.book_append_sheet(new_workbook, worksheet1, "说明")
            this.$XLSX.utils.book_append_sheet(new_workbook, worksheet2, "invalidDict")
            this.$XLSX.writeFile(new_workbook, 'invalidDict-template.xlsx')
        },
        exportDataX: function () {
            let self = this
            // 当没有选项被选中时，默认选中打印当前页
            if (self.selectedItemList.length !== 0) {

                if (self.selectedItemList.length === self.InvalidDictItemData.length) {
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
            self.pageData2Export = self.InvalidDictItemData
            self.expordDataKey++
            self.exportWindowShow = true

        },
        addItem: function () {
            let self = this
            self.formCustom = {
                itemIndex: 1,
                uid: '',
                Items: [{
                    word: '',
                    // operator: localStorage.getItem('kwmUser'),
                    // exStatus: ''
                }]
            }
            self.refreshFlag--
            self.invalidDictItemShow = true

        },
        modifyItem: function () {
            let operator = localStorage.getItem('kwmUser')
            let self = this;
            if (self.currentWord == '') {
                self.$Message.info("无效词不可为空!");
            } else {
                let currentModify = {}
                currentModify.word = self.currentWord
                currentModify.operator = operator
                let allData = currentModify
                self
                    .axios({
                        method: "patch",
                        url: self.baseurl + "InvalidDict/" + self.currentComponent + "/" + self.currentModify._id.$oid,
                        data: allData,
                    })
                    .then((res) => {
                        if (res.data == 'item exist') {
                            self.$Message.info("该无效词已存在!");
                        } else {
                            if (res.data.count !== "") {
                                self.itemCount = res.data.count;
                            }
                            self.InvalidDictItemData = res.data.content;
                            self.currentWord = "";
                            self.$Message.success("修改成功!");
                        }
                    })
                    .catch((err) => {
                        console.log(err);
                        self.$Message.error("修改失败!");
                    });
                this.modifyItemModalShow = false
            }
        },
        cancelAddItem: function () {
            self.modal1 = false;
        },
        editInvalidDictItem: function (row) {
            let self = this
            self.formCustom = {}
            self.$set(self.formCustom, 'uid', row['_id']['$oid'])
            self.$set(self.formCustom, 'itemIndex', 1)
            self.$set(self.formCustom, 'Items', [{
                'word': row['word'],
                // 'operator': localStorage.getItem('kwmUser'),
                //'exStatus': row['exStatus']
            }])
            self.refreshFlag--
            self.invalidDictItemShow = true
        },
        deleteFromInvalidDict: function (word) {
            let self = this

            self
                .axios({
                    method: "delete",
                    url: self.baseurl + "InvalidDict/" + self.currentComponent,
                    data: word,
                })
                .then((res) => {
                    // console.log(res)
                    self.currentPage = 1;
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    self.InvalidDictItemData = res.data.content;
                    self.$Message.success(word + "恢复成功!");
                })
                .catch((err) => {
                    console.log(err);
                    self.$Message.error(word + "恢复失败");
                });
        },
        backToKeyWord: function () {
            let self = this;
            // 目前只需要把 每一行对应的uid取出来，发送到后端进行删除就好了
            // console.log(this.selectedItemList)

            // 当没有选项被选中时，不进行该操作
            if (self.selectedItemList.length === 0) {
                //console.log('no delete')
                self.$Message.info("请选择要恢复的数据");
            } else {
                // let uids = [];

                // 先在前端实现吧
                for (let element in self.selectedItemList) {
                    // uids.push(self.selectedItemList[element]["_id"]["$oid"]);
                    let tempLine = self.selectedItemList[element]
                    // uids.push(self.selectedItemList[element]["word"]);

                    if (tempLine.source === '手动添加' || tempLine.source === '语料分词') {
                        // 1- 来源是 用户添加 或 语料分词， 直接 从停止词典中删除该词
                        self.deleteFromInvalidDict([tempLine.word])
                    } else if (tempLine.source === '用户词') {
                        // 2- 来源是 用户词 , 先将该词加入用户词再将该词从停止词中删除

                        // 2-1 加入用户词
                        let allData = [{
                            word: tempLine.word,
                            categories: [],
                            operator: localStorage.getItem('kwmUser'),
                            // xfrom: localStorage.getItem('kwmdepart')
                        }, ];
                        self
                            .axios({
                                method: "post",
                                url: self.baseurl + "UserDict/" + self.currentComponent,
                                data: allData,
                            })
                            .then((res) => {
                                if (res.data.count !== "") {
                                    self.itemCount = res.data.count;
                                }
                                self.deleteFromInvalidDict([tempLine.word])
                                //self.UserDictItemData = res.data.content;
                                //self.currentWord = "";
                                //self.$Message.success("新增成功!");
                            })
                            .catch((err) => {
                                // console.log(err);
                                self.$Message.error(err.response.data.detail);
                                if (err.response.data.detail.indexOf('以下用户词重复') !== -1) {
                                    self.deleteFromInvalidDict([tempLine.word])
                                }
                            });

                    } else if (tempLine.source === '基础词') {
                        // 3- 来源是 基础词
                        // 3-1 首先将基础词表中，该词状态 改为前状态
                        let myData = {
                            'status': tempLine.exStatus
                        }
                        self.axios({
                                method: 'patch',
                                url: self.baseurl + 'basicWords/' + self.currentComponent + '/' + tempLine.word,
                                data: myData,
                                params: {
                                    'flag': 'word'
                                }

                            })
                            .then(() => {
                                self.deleteFromInvalidDict([tempLine.word])

                            })
                            .catch(err => {
                                // console.log(err)
                                //self.selectedItemList = []
                                //console.log(err.response.data.detail)
                                self.$Message.error(err.response.data.detail);
                            })

                    } else if (tempLine.source === '拓展词') {
                        // 4- 来源是 拓展词
                        let myData = {
                            'status': tempLine.exStatus
                        }
                        self.axios({
                                method: 'patch',
                                url: self.baseurl + 'extendedWords/' + self.currentComponent + '/' + tempLine.word,
                                data: myData,
                                params: {
                                    'flag': 'word'
                                }

                            })
                            .then(() => {
                                self.deleteFromInvalidDict([tempLine.word])

                            })
                            .catch(err => {
                                // console.log(err)
                                //self.selectedItemList = []
                                //console.log(err.response.data.detail)
                                self.$Message.error(err.response.data.detail);
                            })
                    }
                }
                //console.log('xxx', uids)

            }
        },
        exportData: function (type) {
            if (type === 1) {
                this.$refs.table.exportCsv({
                    filename: this.currentComponent,
                    columns: this.columns1.filter((col, index) => {
                        if (index > 0) {
                            return col;
                        }
                    }),
                    data: this.InvalidDictItemData.map((data) => {
                        const target = Object.assign({}, data);
                        // console.log(target)
                        for (let x in target) {
                            target[x] = JSON.stringify(target[x]);
                            target[x] = target[x].replace(/,/g, ";");
                            // target[x] = target[x].replace(/"/g, "'");
                        }
                        return target;
                    }),
                });
            }
        },
        searchInvlidItem: function () {
            let self = this
            let data = {
                keyword: self.searchWord
            }
            self
                .axios({
                    method: "get",
                    url: self.baseurl + "InvalidDict/" + self.currentComponent + "?keyword=" + self.searchWord,
                    data: data,
                })
                .then((res) => {
                    // console.log(res)
                    self.currentPage = 1;
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    //console.log(res.data.content)
                    self.InvalidDictItemData = res.data.content;
                })
                .catch((err) => {
                    console.log(err)
                    self.$Message.error("搜索失败");
                });
        },
        handleFilter: function (column) {
            console.log(column)
            let self = this
            let chekced = {
                'key': column['key'],
                'checked': column['_filterChecked']
            }
            if (chekced.key === 'operator') {
                self.operatorChecked = chekced['checked']
            } else if (chekced.key === 'source') {
                self.sourceChecked = chekced['checked']
            }
            self.currentPage = 1
            let params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'operatorFilter': encodeURIComponent(self.operatorChecked),
                'sourceFilter': encodeURIComponent(self.sourceChecked),
                'searchItem': self.searchItem.toLowerCase(),

            }

            self.fetchItemsES(params)
        },
        getUserInformation: function () {
            let self = this
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Account/AllUsers',
                })
                .then(res => {
                    for (let ele in res.data.content) {
                        self.userList.push({
                            'label': res.data.content[ele].account,
                            'value': res.data.content[ele].account
                        })
                    }
                    // console.log('projetcCategoriesList',self.projetcCategoriesList)
                    self.columns1[3].filters = self.userList // 必须要设置一下 ，目录列表
                })
                .catch(err => {
                    console.log(err)
                })
        },
        TimeChange: function (daterange) {
            let self = this
            //console.log('time changed')
            //console.log(daterange)
            self.dateRange = daterange

            //日期被重新筛选，激发重新搜索
            let params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'operatorFilter': encodeURIComponent(self.operatorChecked),
                'sourceFilter': encodeURIComponent(self.sourceChecked),
                'searchItem': self.searchItem.toLowerCase(),

            }
            self.fetchItemsES(params)
        },
        deleteItem: function () {
            let self = this
            let items = [];
            items.push(self.currentModify["word"]);
            // console.log(uids)
            self
                .axios({
                    method: "delete",
                    url: self.baseurl + "InvalidDict/" + self.currentComponent,
                    data: items,
                })
                .then((res) => {
                    // console.log(res)
                    self.currentPage = 1;
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    self.InvalidDictItemData = res.data.content;
                    self.$Message.success("删除成功!");
                })
                .catch((err) => {
                    console.log(err);
                    self.$Message.error("删除失败");
                });
            this.modifyItemModalShow = false
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

            let temp = {
                //itemIndex: initFlag,
                //uid: '',
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
                // console.log('workbook-url',workbook.Sheets.invalidWords)
                // 前一行是 header，所以略过。第二行是空行，空行在读的时候已经被 略过
                let dataFormat = self.$XLSX.utils.sheet_to_json(workbook.Sheets.invalidDict, {
                    header: 1,
                    blankrows: false
                }).slice(2)
                //console.log('dataFormat',dataFormat)
                for (let ele in dataFormat) {
                    let lineData = dataFormat[ele]
                    try {
                        //initFlag++
                        temp.Items.push({
                            'word': lineData[0].trim(),
                            'operator': localStorage.getItem('kwmUser'),
                            'source': '手动添加',
                            'exStatus': ''
                        })
                    } catch (error) {
                        self.$Message.error(error.message);
                    }
                }

                // 如果有 有效数据，直接上传，否则弹窗提示
                if (temp.Items.length > 0) {
                    self.createInvalidWords(temp.Items)
                } else {
                    self.$Message.info('未包含有效数据!');
                }
            }
            return false // 返回false 代表 不上传
        },
        handleSelectRow: function () {
            this.selectedItemList = this.$refs.table.getSelection();
            // console.log(this.selectedItemList)
        },
        fetchItems: function (Params = {}) {
            let self = this;
            self.loading = true
            self
                .axios({
                    method: "get",
                    url: self.baseurl + "InvalidDict/" + self.currentComponent,
                    params: Params,
                })
                .then((res) => {
                    //console.log(res)
                    // self.currentPage = 1
                    self.loading = false
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    //console.log(res.data.content)
                    self.InvalidDictItemData = res.data.content;
                })
                .catch((err) => {
                    console.log(err);
                });
        },
        fetchItemsES: function (Params = {}) {
            let self = this;
            self.loading = true
            self
                .axios({
                    method: "get",
                    url: self.baseurl + "InvalidDict/es/" + self.currentComponent,
                    params: Params,
                })
                .then((res) => {
                    //console.log(res)
                    // self.currentPage = 1
                    self.loading = false
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    //console.log(res.data.content)
                    self.InvalidDictItemData = res.data.content;
                })
                .catch((err) => {
                    console.log(err);
                });
        },
        pageChange: function (pageIndex) {
            // console.log(pageIndex)
            let self= this
            self.currentPage = pageIndex;
            let params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'operatorFilter': encodeURIComponent(self.operatorChecked),
                'sourceFilter': encodeURIComponent(self.sourceChecked),
                'searchItem': self.searchItem.toLowerCase(),

            }
            self.fetchItems(params);
        },
        pageSizeChange: function (pageSize) {
            let self = this
            self.pageSize = pageSize;
            self.currentPage = 1;
            let params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'operatorFilter': encodeURIComponent(self.operatorChecked),
                'sourceFilter': encodeURIComponent(self.sourceChecked),
                'searchItem': self.searchItem.toLowerCase(),

            }
            self.fetchItems(params);
        }
    },
}
</script>

<style scoped>
.invalid-table {
    font-weight: 450;
    overflow: auto
}

.my-title {
    display: flex;
    margin-top: 5px;
    margin-bottom: 5px;
    align-items: center;
    justify-content: space-between
}

>>>.ivu-table-cell {
    padding: 5px !important
}

>>>.ivu-icon.ivu-icon-ios-search.ivu-input-icon.ivu-input-icon-normal.ivu-input-search-icon,
.ivu-icon.ivu-icon-ios-close-circle.ivu-input-icon.ivu-input-icon-clear.ivu-input-icon-normal {
    padding-top: 0px !important
}
</style>
