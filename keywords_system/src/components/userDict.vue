<template>
<div class="my-container">
    <div class="my-title">
        <i-button type="error" icon="md-trash" @click="deleteConfirm">删除</i-button>
        <i-button type="warning" @click="exportDataX()" icon="md-download">导出数据</i-button>
        <i-button type="primary" icon="md-add" @click="addItem()">在线添加</i-button>
        <i-button type="primary" @click="downloadTemplate" icon="md-copy">下载模板</i-button>
        <i-upload class="Url-batchUpload-button" ref="upload" action :show-upload-list="false" :before-upload="handleBeforeUpload">
            <i-button class="Url-part114 Url-newItems-button" type="primary" icon="md-cloud-upload" @click="addInvalidDictItems">批量添加</i-button>
        </i-upload>
    </div>

    <i-page :total="itemCount" :current="currentPage" placement="bottom" :page-size="pageSize" :page-size-opts="[10,20,30,40,50,100]" size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />
    <i-table class="userDict-table" :columns="columns1" :data="UserDictItemData" :loading="loading" @on-filter-change="handleFilter" @on-selection-change="handleSelectRow()" @on-sort-change="handleSort" ref="table" stripe border>
        <template slot-scope="{ row }" slot="action">
            <div class="Url-actions">
                <i-button type="success" size="small" style="margin-right: 5px" @click="editUserDictItem(row)">修改</i-button>
            </div>
        </template>
    </i-table>
    <i-page :total="itemCount" :current="currentPage" placement="top" :page-size="pageSize" :page-size-opts="[10,20,30,40,50,100]" size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />

    <!--弹出框都在此地-->
    <i-userDictItemPage :key="refreshFlag" :formCustom2="JSON.parse(JSON.stringify(formCustom))" :userDictItemShow.sync="userDictItemShow" @createUserWords="createUserWords" @deleteUserDictWordItem="handledeleteUserWordItem" @UpdateUserWords="handleUpdateUserWordItem"></i-userDictItemPage>
    <i-exportData :key="expordDataKey" :pageSize="pageSize" :selectedFlag="selectedFlag" :selected1="selected1" :pageData2Export="pageData2Export" :exportWindowShow.sync="exportWindowShow"></i-exportData>

</div>
</template>

<script>
import exportData from '@/components/userDict/exportData.vue'
import userDictItemPage from '@/components/userDict/userDictItemPage.vue'
import userDictSearch from '@/components/userDict/userDictSearch.vue'

import {
    mapState,
    mapMutations
} from "vuex";
export default {
    name: 'userDict',
    data() {
        var global = this // 如果不这样， render 中找不到 正确的 this
        return {
            exportWindowShow: false,
            pageData2Export: [],
            selected1: '当前选中',
            selectedFlag: [],
            expordDataKey: 20,
            userDictItemShow: false,
            refreshFlag: 1000,
            excelNoteData: [
                ['', '使用前必看！'],
                ['', ''],
                [1, '请将数据按照示例格式填写在 userdDict sheet中'],
                [2, '不要修改userDict sheet的名称，否则会出错'],
                [3, '每行填写一个词'],
                [4, '从第3行开始写']
            ],
            excelTemplateData: {
                data: [
                    ["用户词", "出处"],
                    ["", ""],
                    ["毁灭", "电影名词"],
                    ["宇宙", "科学技术"]
                ]
            },
            newItemModalShow: false,
            modifyItemModalShow: false,
            currentWord: "",
            currentItem: undefined,
            searchWord: '',
            userList: [],
            dateRange: ['', ''],
            operatorChecked: [],
            wordLengthChecked: [],
            categoryChecked: [],
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
                    width: 45,
                    align: 'center',
                    //sortable: true,
                    resizable: true,
                    fixed: 'left'
                },
                {
                    title: "用户词",
                    key: "word",
                    align: "center",
                    minWidth: 80,
                    sortable: false,
                    resizable: true,
                    renderHeader(h) {
                        return h('span', [
                            h('span', '用户词'),
                            h('i-poptip', {
                                    props: {
                                        title: "用户词全文搜索",
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
                                    h(userDictSearch, {
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
                    width: 90,
                    resizable: true,
                    renderHeader(h) {
                        return h('span', [
                            h('span', '生成时间'),
                            h('i-poptip', {
                                    props: {
                                        title: "日期过滤",
                                        content: "content",
                                        placement: "bottom-start",
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
                    title: "出处",
                    key: "source",
                    align: "center",
                    resizable: true
                },
                {
                    title: "操作人",
                    key: "operator",
                    align: "left",
                    filters: [],
                    filterMethod(value) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        //if (row.status === value){
                        return value //什么都不做，由专门的函数进行后端筛选
                        //}
                    },
                    resizable: true,
                },
                {
                    title: "长度",
                    key: "length",
                    align: "center",
                    width: 80,
                    sortable: 'custom',
                    resizable: true,
                    filters: [{
                        'label': '0-2',
                        'value': '1'
                    }, {
                        'label': '2-4',
                        'value': '2'
                    }, {
                        'label': '4-8',
                        'value': '3'
                    }, {
                        'label': '8以上',
                        'value': '4'
                    }],
                    filterMethod(value) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        //if (row.status === value){
                        return value //什么都不做，由专门的函数进行后端筛选
                        //}
                    },
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
            UserDictItemData: [],
            formCustom: {},
            sortDict: {},
        };
    },
    computed: {
        ...mapState([
            "baseurl",
            "currentComponent"
        ]),
    },
    mounted() {
        let params = {
            'currentPage': this.currentPage,
            'pageSize': this.pageSize,
        }
        this.fetchItems(params); // 获取当前
        this.getUserInformation()
    },
    components: {
        'i-exportData': exportData,
        'i-userDictItemPage': userDictItemPage
    },
    methods: {
         ...mapMutations(['changeSearchDisplay']),
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
            if (Object.keys(sortDict).length !== 0) {
                // 发送排序请求
                self.currentPage = 1
                let Params = {
                    'currentPage': self.currentPage,
                    'pageSize': self.pageSize,
                    'dateRange': encodeURIComponent(self.dateRange),
                    'operatorFilter': encodeURIComponent(self.operatorChecked),
                    'categoryFilter': encodeURIComponent(self.categoryChecked),
                    'searchItem': self.searchItem.toLowerCase(),
                    'wordLength': encodeURIComponent(self.wordLengthChecked),
                    'sortDict': JSON.stringify(self.sortDict)
                }
                //console.log(Params)
                self.fetchItemsES(Params)
            } else {
                self.$Message.info('排序条件不满足!');
            }
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
            self.fetchItemsES(Params)
        },
        batchSearch: function (part) {
            // 输入特定查询，按下回车键或 搜索按钮时 ，触发，会返回所有符合条件的项目 或为空
            let self = this
            //console.log('batchSearch')
            self.searchItem = part
            self.searchResult = []
            // 下面进行 batchSearch
            self.changeSearchDisplay(part)
            self.currentPage = 1
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'dateRange':encodeURIComponent(self.dateRange),'wordPart':self.searchItem.toLowerCase() ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'statusFilter': encodeURIComponent(self.statusChecked)}
            let params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'operatorFilter': encodeURIComponent(self.operatorChecked),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'searchItem': self.searchItem.toLowerCase(),
                'wordLength': encodeURIComponent(self.wordLengthChecked),
                'sortDict': JSON.stringify(self.sortDict)

            }

            // console.log(Params)
            self.fetchItemsES(params)

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
            // 目前后端是  依据 word 字段 去进行 删除操作的
            // 当没有选项被选中时，不进行该操作
            let words = []
            for (let element in self.selectedItemList) {
                words.push({
                    'word': self.selectedItemList[element]['word']
                })

            }
            //console.log(words)
            self.handledeleteUserWordItem(words)
        },
        handledeleteUserWordItem: function (words) {
            let self = this
            // 联系后台，进行删除
            self.axios({
                    method: 'delete',
                    url: self.baseurl + 'UserDict/' + self.currentComponent,
                    data: words
                })
                .then(res => {
                    // console.log(res)
                    self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.selectedItemList = []
                    self.UserDictItemData = res.data.content
                })
                .catch(err => {
                    // console.log(err)
                    console.log(err.response.data.detail)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        handleUpdateUserWordItem: function (newData) {
            let self = this
            //console.log('newData', newData)
            let pageParams = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            self.axios({
                    method: "patch",
                    url: self.baseurl + 'UserDict/' + self.currentComponent + '/' + newData.uid,
                    data: newData.data,
                    params: pageParams
                })
                .then((res) => {
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    self.UserDictItemData = res.data.content;
                    self.$Message.success("修改成功!");

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
        createUserWords: function (DATA) {
            // 创建用户词

            let self = this;
            //console.log('DATA', DATA)
            self.currentPage = Math.ceil((self.itemCount + 1) / self.pageSize)
            let pageParams = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            self.axios({
                    method: "post",
                    url: self.baseurl + "UserDict/" + self.currentComponent,
                    data: DATA,
                    params: pageParams
                })
                .then((res) => {
                    //console.log(res)
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    self.UserDictItemData = res.data.content;
                    self.$Message.success("新增成功!");

                })
                .catch((err) => {
                    console.log(err);
                    //self.$Message.error("新增失败!");
                    self.$Message.error({
                        content: JSON.stringify(err.response.data.detail),
                        duration: 0,
                        closable: true
                    })
                })
        },
        downloadTemplate: function () {
            // 向 excelNoteData 中添加 目录数据

            let worksheet1 = this.$XLSX.utils.aoa_to_sheet(this.excelNoteData)
            let worksheet2 = this.$XLSX.utils.aoa_to_sheet(this.excelTemplateData.data)
            let new_workbook = this.$XLSX.utils.book_new()
            this.$XLSX.utils.book_append_sheet(new_workbook, worksheet1, "说明")
            this.$XLSX.utils.book_append_sheet(new_workbook, worksheet2, "UserDict")
            this.$XLSX.writeFile(new_workbook, 'UserDict-template.xlsx')
        },
        addItem: function () {
            let self = this
            self.formCustom = {
                itemIndex: 1,
                uid: '',
                Items: [{
                    word: '',
                    source: ''
                    // operator: localStorage.getItem('kwmUser'),
                    // exStatus: ''
                }]
            }
            self.refreshFlag--
            self.userDictItemShow = true

        },
        modifyItem: function () {
            let operator = localStorage.getItem('kwmUser')
            let self = this;
            if (self.currentWord == '') {
                self.$Message.info("用户词不可为空!");
            } else {
                let currentModify = {
                    word: self.currentWord,
                    operator: operator,
                    //xfrom: localStorage.getItem('kwmdepart')
                }
                let allData = currentModify
                self
                    .axios({
                        method: "put",
                        url: self.baseurl +
                            "UserDict/" +
                            self.currentComponent +
                            "/" +
                            self.currentModify._id.$oid,
                        data: allData,
                    })
                    .then((res) => {

                        if (res.data.count !== "") {
                            self.itemCount = res.data.count;
                        }
                        self.UserDictItemData = res.data.content;
                        self.currentWord = "";
                        self.$Message.success("修改成功!");

                    })
                    .catch((err) => {
                        console.log(err);
                        // self.$Message.error("修改失败!");
                        self.$Message.error({
                            content: JSON.stringify(err.response.data.detail),
                            duration: 0,
                            closable: true
                        });
                    });
                this.modifyItemModalShow = false
            }
        },
        editUserDictItem: function (row) {
            let self = this
            self.formCustom = {
                itemIndex: 1,
                uid: row['_id']['$oid'],
                Items: [{
                    word: row.word,
                    source: row.source,
                    category: row.category
                }]
            }
            self.refreshFlag--
            self.userDictItemShow = true

        },
        exportDataX: function () {
            let self = this
            // 当没有选项被选中时，默认选中打印当前页
            if (self.selectedItemList.length !== 0) {

                if (self.selectedItemList.length === self.UserDictItemData.length) {
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
            self.pageData2Export = self.UserDictItemData
            self.expordDataKey++
            self.exportWindowShow = true

        },
        addInvalidDictItems: function () {},
        searchInvlidItem: function () {
            let self = this
            let data = {
                keyword: self.searchWord
            }
            self
                .axios({
                    method: "get",
                    url: self.baseurl + "UserDict/" + self.currentComponent + "?keyword=" + self.searchWord,
                    data: data,
                })
                .then((res) => {
                    // console.log(res)
                    self.currentPage = 1;
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    //console.log(res.data.content)
                    self.UserDictItemData = res.data.content;
                })
                .catch((err) => {
                    console.log(err)
                    self.$Message.error("搜索失败");
                });
        },
        handleFilter: function (column) {
            let self = this
            let chekced = {
                'key': column['key'],
                'checked': column['_filterChecked']
            }
            if (chekced.key == 'length') {
                self.wordLengthChecked = chekced['checked']
            } else if (chekced.key == 'operator') {
                self.operatorChecked = chekced['checked']
            } else if (chekced.key == 'category') {
                self.categoryChecked = chekced['checked']
            }
            self.currentPage = 1
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'searchItem': self.searchItem.toLowerCase(),
                'operatorFilter': encodeURIComponent(self.operatorChecked),
                'wordLengthFilter': encodeURIComponent(self.wordLengthChecked),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }
            //console.log('Params', Params)
            self.fetchItemsES(Params)
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
                    self.columns1[5].filters = self.userList // 必须要设置一下 ，目录列表
                })
                .catch(err => {
                    console.log(err)
                })
        },
        TimeChange: function (daterange) {
            let self = this
            self.dateRange = daterange

            //日期被重新筛选，激发重新搜索
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'searchItem': self.searchItem.toLowerCase(),
                'operatorFilter': encodeURIComponent(self.operatorChecked),
                'wordLengthFilter': encodeURIComponent(self.wordLengthChecked),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }
            self.fetchItemsES(Params)
        },
        deleteItem: function () {
            let self = this
            let items = [];
            items.push({
                word: self.currentModify["word"]
            });
            // console.log(uids)
            self
                .axios({
                    method: "delete",
                    url: self.baseurl + "UserDict/" + self.currentComponent,
                    data: items,
                })
                .then((res) => {
                    // console.log(res)
                    self.currentPage = 1;
                    if (res.data.count !== "") {
                        self.itemCount = res.data.count;
                    }
                    self.UserDictItemData = res.data.content;
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

            let temp = []
            let bad = [] // 存放 有问题的数据

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
                let dataFormat = self.$XLSX.utils.sheet_to_json(workbook.Sheets.UserDict, {
                    header: 1,
                    blankrows: false
                }).slice(2)
                //console.log('dataFormat',dataFormat)
                for (let ele in dataFormat) {
                    let lineData = dataFormat[ele]
                    //console.log('lineData', lineData)
                    try {
                        //initFlag++
                        if (lineData[0] && lineData[1]) {
                            // word 和 目录 都不为空，则添加到 正常 list
                            temp.push({
                                'word': lineData[0].trim(),
                                'operator': localStorage.getItem('kwmUser'),
                                'category': lineData[1].trim().replace(/，/g, ',').split(','),
                                'source': lineData[2]
                            })
                        } else {
                            // 否则，若至少一个为空，则添加到 bad list，然后将 badlist展示出来，让用户修改
                            let word = ''
                            let category = ''

                            if (lineData[0]) {
                                word = lineData[0].trim()
                            }

                            if (lineData[1]) {
                                category = lineData[1].trim().replace(/，/g, ',').split(',')
                            }
                            bad.push({
                                'word': word,
                                'operator': localStorage.getItem('kwmUser'),
                                'category': category,
                                'source': lineData[2]
                            })
                        }
                    } catch (error) {
                        self.$Message.error(error.message);
                    }
                }

                // 如果有 bad 为空，则，直接上传，否则弹窗提示
                //console.log('temp,bad', temp, bad)
                if (bad.length === 0) {
                    if (temp.length > 0) {
                        self.createUserWords(temp)
                    } else {
                        self.$Message.info('未包含有效数据!');
                    }

                } else {
                    if (temp.length > 0) {
                        // 先把 有效的上传，然后再编辑 有错的
                        self.createUserWords(temp)
                        self.formCustom = {
                            itemIndex: bad.length,
                            uid: '',
                            Items: bad
                        }
                    } else {
                        // 弹窗 让用户 修改
                        self.formCustom = {
                            itemIndex: bad.length,
                            uid: '',
                            Items: bad
                        }
                    }
                    self.refreshFlag--
                    self.userDictItemShow = true
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
            self.axios({
                    method: "get",
                    url: self.baseurl + "UserDict/" + self.currentComponent,
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
                    self.UserDictItemData = res.data.content;
                })
                .catch((err) => {
                    console.log(err);
                });
        },

        fetchItemsES: function (Params = {}) {
            let self = this;
            self.loading = true
            self.axios({
                    method: "get",
                    url: self.baseurl + "UserDict/es/" + self.currentComponent,
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
                    self.UserDictItemData = res.data.content;
                })
                .catch((err) => {
                    console.log(err);
                });
        },

        pageChange: function (pageIndex) {
            // console.log(pageIndex)
            let self = this
            self.currentPage = pageIndex
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'searchItem': self.searchItem.toLowerCase(),
                'operatorFilter': encodeURIComponent(self.operatorChecked),
                'wordLengthFilter': encodeURIComponent(self.wordLengthChecked),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }

            self.fetchItemsES(Params);
        },
        pageSizeChange: function (pageSize) {
            let self = this
            self.pageSize = pageSize;
            self.currentPage = 1;
            // console.log(pageSize)
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'dateRange': encodeURIComponent(self.dateRange),
                'searchItem': self.searchItem.toLowerCase(),
                'operatorFilter': encodeURIComponent(self.operatorChecked),
                'wordLengthFilter': encodeURIComponent(self.wordLengthChecked),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'sortDict': JSON.stringify(self.sortDict)
            }
            self.fetchItemsES(Params);
        },
    },
}
</script>

<style scoped>
.my-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 5px;
}

.userDict-table {
    font-weight: 450;
    overflow: auto
}

>>>.ivu-table-cell {
    padding: 5px !important
}

>>>.ivu-icon.ivu-icon-ios-search.ivu-input-icon.ivu-input-icon-normal.ivu-input-search-icon,
.ivu-icon.ivu-icon-ios-close-circle.ivu-input-icon.ivu-input-icon-clear.ivu-input-icon-normal {
    padding-top: 0px !important
}
</style>
