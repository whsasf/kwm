<template>
<div>
    <div class="extendedWords-button-group">
        <div class="p11">
            <i-draggable class="dragable-warp" v-model="sortItems" @start="drag=true" @end="drag=false" @change="onChange">
                <div class="dragablex" v-for="(item,index) in sortItems" :key="index">
                    <div class="label">{{item.name}}</div>
                    <i-select v-model="item.model" style="width:65px" @on-change="onChange">
                        <i-option v-for="item2 in sortList" :value="item2.value" :key="item2.value">{{ item2.label }}</i-option>
                    </i-select>
                </div>
            </i-draggable>
            <i-button class="basicWords-export-button" type="warning" @click="exportDataX">
                <i-icon type="md-download"></i-icon> 导出数据
            </i-button>
        </div>

        <div class="p2">
            <div class="p21">
                <i-button type="error" v-if="false" icon="md-trash" @click="deleteConfirm">删除</i-button>
                <i-page class="page" :total="itemMuCount" placement="bottom" :current="currentPage" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />
                <i-button class="new" height="200" style="color: #fff;background-color: #54616f" @click="setStopWord">设为停止词</i-button>
                <i-button type="success" class="calculate" @click="calculateInherit">计算母词统计数据</i-button>
            </div>
            <i-button height="200" style="color: #fff;background-color: #7b5ae4" @click="setInvalidWord">设为无效词</i-button>
        </div>

        <div class="xx2">
            <i-button v-if="false" class="new" type="primary" icon="md-add-circle" @click="addItem">在线添加</i-button>
        </div>

    </div>

    <i-radioGroup v-model="viewSelected" type="button" @on-change="setCurrentView">
        <i-radio label="默认视图">
        </i-radio>
        <i-radio label="主题视图">
        </i-radio>
        <i-radio label="母词视图">
        </i-radio>
    </i-radioGroup>

    <i-table class="basicWords-table" row-key="id" :load-data="handleLoadData" :columns="columns1" :data="extendedWordsMuItemData" :loading="tableLoading" @on-selection-change="handleSelectRow()" ref="table" stripe border @on-filter-change="handleFilter" @on-sort-change="handleSort">
        <template slot-scope="{ row }" slot="action">
            <div>
                <i-button v-if="row.category" type="primary" size="small" style="margin-right: 5px" @click="editItem(row)">修改</i-button>
                <i-button type="success" size="small" style="margin-right: 5px" @click="seeExpandTree(row)">查看拓词树</i-button>
            </div>
        </template>
    </i-table>

    <i-page class="page" :total="itemMuCount" :current="currentPage" placement="top" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />

    <!--弹出框都在此地-->
    <i-extendWordItemPage :key="refreshFlag" :rawCategories="rawCategories" :rawTags="rawTags" :formCustom2="JSON.parse(JSON.stringify(formCustom))" :extendedWordItemShow.sync="extendedWordItemShow" @createExtendedWords="createExtendedWords" @deleteExtendedWordItem="handledeleteExtendedWordItem" @UpdateExtendedWords="handleUpdateExtendedWordItem"></i-extendWordItemPage>
    <i-topoTree :treeType="treeType" :topoTreeKeyWord="topoTreeKeyWord" :key="topoTreeKey" :topoTreeShow.sync="topoTreeShow"></i-topoTree>
    <i-exportData :key="expordDataKey" :pageSize="pageSize" :selectedFlag="selectedFlag" :selected1="selected1" :pageData2Export="pageData2Export" :exportWindowShow.sync="exportWindowShow"></i-exportData>
</div>
</template>

<script>
import {
    mapState,
    mapMutations
} from 'vuex'
import extendedWordItemPage from '@/components/extendedWords/extendedWordItemPage.vue'
import extendedWordSearch from '@/components/extendedWords/extendedWordSearch.vue'
import topoTree from '@/components/topoTree.vue'
import exportData from '@/components/extendedWords/exportData.vue'

export default {
    name: 'extendedWordsInherit',
    data() {
        var global = this // 如果不这样， render 中找不到 正确的 this
        return {
            extendedWordsMuItemData: [],
            itemMuCount: 0,
            viewSelected: '母词视图',
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
                    "name": "百度指数-移动",
                    "id": 'baiduIndexM',
                    'model': 'default',
                },

                {
                    "name": "搜索次数-移动",
                    "id": 'searchCountM',
                    'model': 'default'
                },
                {
                    "name": "竞价-移动",
                    "id": 'bidPriceM',
                    'model': 'default'
                },
                {
                    "name": "百度指数",
                    "id": 'baiduIndex',
                    'model': 'default',
                },

                {
                    "name": "搜索次数",
                    "id": 'searchCount',
                    'model': 'default'
                },
                {
                    "name": "竞价",
                    "id": 'bidPrice',
                    'model': 'default'
                },

            ],
            treeType: 'extended',
            selected1: '当前选中',
            selectedFlag: [],
            expordDataKey: -20,
            pageData2Export: [],
            exportWindowShow: false,
            topoTreeKeyWord: '',
            topoTreeKey: 200,
            topoTreeShow: false,
            rawTags: ['tag1', 'tag2', 'tag3'],
            searchItem: '',
            searchResult: [],
            dataRange: ['', ''],
            categoryChecked: [],
            bidPriceChecked: [],
            baiduIndexChecked: [],
            searchCountChecked: [],
            bidPriceMChecked: [],
            baiduIndexMChecked: [],
            searchCountMChecked: [],
            usageTagChecked: [],
            statusChecked: [],
            lengthChecked: [],
            sortDict: {},
            refreshFlag: 1000,
            extendedWordItemShow: false,
            selectedItemList: [],
            rawCategories: [],
            projetcCategoriesList: [],
            projetcUsageTagsList: [],
            formCustom: {},
            itemCount: 0,
            currentPage: 1,
            pageSize: 10,
            extendedWordsItemData: [],
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
                    title: '拓展词',
                    key: 'word',
                    align: 'left',
                    minWidth: 150,
                    tree: true,
                    fixed: 'left',
                    resizable: true,
                    render: (h, params) => {
                        if (params.row.children) {
                            return h('span', {
                                style: {
                                    'font-weight': 800,
                                    'color': '#212891'
                                }
                            }, params.row.word + ' ( ' + params.row.children.length + ' )')
                        } else {
                            return h('span', params.row.word)
                        }
                    },
                    renderHeader(h) {
                        return h('span', [
                            h('span', '拓展词'),
                            h('i-poptip', {
                                    props: {
                                        title: "母词过滤",
                                        content: "content",
                                        placement: "right-start",
                                        transfer: true,
                                        trigger: 'click',
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
                                    h(extendedWordSearch, {
                                        slot: "content",
                                        props: {
                                            wordItem: 'mword'
                                        },
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
                    }

                },
                {
                    title: '搜索次数(周)-移动',
                    key: 'searchCountM',
                    align: 'center',
                    // sortable: 'custom',
                    minWidth: 150,
                    // 1 -> [0,0.3], 2 -> [0.3,0.5], 3 -> [0.5,1], 4 -> [1,5],5 -> [5,10], 6 -> [10,20], 7 -> [20,50]
                    filters: [{
                        'label': '0-20',
                        'value': '1'
                    }, {
                        'label': '20-50',
                        'value': '2'
                    }, {
                        'label': '50-100',
                        'value': '3'
                    }, {
                        'label': '100-200',
                        'value': '4'
                    }, {
                        'label': '200-500',
                        'value': '5'
                    }, {
                        'label': '500-1000',
                        'value': '6'
                    }, {
                        'label': '1000-2000',
                        'value': '7'
                    }, {
                        'label': '2000-4000',
                        'value': '8'
                    }, {
                        'label': '4000-7000',
                        'value': '9'
                    }, {
                        'label': '7000-10000',
                        'value': '10'
                    }, {
                        'label': '10000-20000',
                        'value': '11'
                    }, {
                        'label': '20000-2000000',
                        'value': '12'
                    }],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        return row //什么都不做，由专门的函数进行后端筛选
                    },
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params.row)
                        if (!params.row.category) {
                            return h('p', {
                                style: {
                                    'color': 'red',
                                    'font-weight': 'bold'
                                }
                            }, params.row.searchCountM)

                        } else {
                            return h('p', params.row.searchCountM)
                        }
                    }
                },
                {
                    title: '竞价-移动',
                    key: 'bidPriceM',
                    align: 'center',
                    minWidth: 90,
                    //sortable: 'custom',
                    filters: [{
                        'label': '0-20',
                        'value': '1'
                    }, {
                        'label': '20-50',
                        'value': '2'
                    }, {
                        'label': '50-100',
                        'value': '3'
                    }, {
                        'label': '100-200',
                        'value': '4'
                    }, {
                        'label': '200-500',
                        'value': '5'
                    }, {
                        'label': '500-1000',
                        'value': '6'
                    }, {
                        'label': '1000-2000',
                        'value': '7'
                    }, {
                        'label': '2000-4000',
                        'value': '8'
                    }, {
                        'label': '4000-7000',
                        'value': '9'
                    }, {
                        'label': '7000-10000',
                        'value': '10'
                    }, {
                        'label': '10000-20000',
                        'value': '11'
                    }, {
                        'label': '20000-2000000',
                        'value': '12'
                    }],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        return row //什么都不做，由专门的函数进行后端筛选
                    },
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params.row)
                        if (!params.row.category) {
                            return h('p', {
                                style: {
                                    'color': 'green',
                                    'font-weight': 'bold'
                                }
                            }, Math.floor(params.row.bidPriceM * 100) / 100)

                        } else {
                            return h('p', Math.floor(params.row.bidPriceM * 100) / 100)
                        }
                    }
                },
                {
                    title: '百度指数-移动',
                    key: 'baiduIndexM',
                    align: 'center',
                    //sortable: 'custom',
                    minWidth: 130,
                    // 1 -> [0,20],3 -> [20,50], 4 -> [50,100],5 -> [100,200], 6 -> [200,500], 7 -> [500,1000] [1000,2000] ,[2000,4000],[4000,7000],[7000-10000],[10000,20000],[20000,2000000]
                    filters: [{
                        'label': '0-20',
                        'value': '1'
                    }, {
                        'label': '20-50',
                        'value': '2'
                    }, {
                        'label': '50-100',
                        'value': '3'
                    }, {
                        'label': '100-200',
                        'value': '4'
                    }, {
                        'label': '200-500',
                        'value': '5'
                    }, {
                        'label': '500-1000',
                        'value': '6'
                    }, {
                        'label': '1000-2000',
                        'value': '7'
                    }, {
                        'label': '2000-4000',
                        'value': '8'
                    }, {
                        'label': '4000-7000',
                        'value': '9'
                    }, {
                        'label': '7000-10000',
                        'value': '10'
                    }, {
                        'label': '10000-20000',
                        'value': '11'
                    }, {
                        'label': '20000-2000000',
                        'value': '12'
                    }],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        return row //什么都不做，由专门的函数进行后端筛选
                    },
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params.row)
                        if (!params.row.category) {
                            return h('p', {
                                style: {
                                    'color': 'blue',
                                    'font-weight': 'bold'
                                }
                            }, Math.floor(params.row.baiduIndexM * 100) / 100)

                        } else {
                            return h('p', Math.floor(params.row.baiduIndexM * 100) / 100)
                        }
                    }
                },
                {
                    title: '搜索次数(周)',
                    key: 'searchCount',
                    align: 'center',
                    // sortable: 'custom',
                    minWidth: 130,
                    // 1 -> [0,0.3], 2 -> [0.3,0.5], 3 -> [0.5,1], 4 -> [1,5],5 -> [5,10], 6 -> [10,20], 7 -> [20,50]
                    filters: [{
                        'label': '0-20',
                        'value': '1'
                    }, {
                        'label': '20-50',
                        'value': '2'
                    }, {
                        'label': '50-100',
                        'value': '3'
                    }, {
                        'label': '100-200',
                        'value': '4'
                    }, {
                        'label': '200-500',
                        'value': '5'
                    }, {
                        'label': '500-1000',
                        'value': '6'
                    }, {
                        'label': '1000-2000',
                        'value': '7'
                    }, {
                        'label': '2000-4000',
                        'value': '8'
                    }, {
                        'label': '4000-7000',
                        'value': '9'
                    }, {
                        'label': '7000-10000',
                        'value': '10'
                    }, {
                        'label': '10000-20000',
                        'value': '11'
                    }, {
                        'label': '20000-2000000',
                        'value': '12'
                    }],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        return row //什么都不做，由专门的函数进行后端筛选
                    },
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params.row)
                        if (!params.row.category) {
                            return h('p', {
                                style: {
                                    'color': 'red',
                                    'font-weight': 'bold'
                                }
                            }, params.row.searchCount)

                        } else {
                            return h('p', params.row.searchCount)
                        }
                    }
                },
                {
                    title: '竞价',
                    key: 'bidPrice',
                    align: 'center',
                    minWidth: 90,
                    //sortable: 'custom',
                    filters: [{
                        'label': '0-20',
                        'value': '1'
                    }, {
                        'label': '20-50',
                        'value': '2'
                    }, {
                        'label': '50-100',
                        'value': '3'
                    }, {
                        'label': '100-200',
                        'value': '4'
                    }, {
                        'label': '200-500',
                        'value': '5'
                    }, {
                        'label': '500-1000',
                        'value': '6'
                    }, {
                        'label': '1000-2000',
                        'value': '7'
                    }, {
                        'label': '2000-4000',
                        'value': '8'
                    }, {
                        'label': '4000-7000',
                        'value': '9'
                    }, {
                        'label': '7000-10000',
                        'value': '10'
                    }, {
                        'label': '10000-20000',
                        'value': '11'
                    }, {
                        'label': '20000-2000000',
                        'value': '12'
                    }],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        return row //什么都不做，由专门的函数进行后端筛选
                    },
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params.row)
                        if (!params.row.category) {
                            return h('p', {
                                style: {
                                    'color': 'green',
                                    'font-weight': 'bold'
                                }
                            }, Math.floor(params.row.bidPrice * 100) / 100)

                        } else {
                            return h('p', Math.floor(params.row.bidPrice * 100) / 100)
                        }
                    }
                },
                {
                    title: '百度指数',
                    key: 'baiduIndex',
                    align: 'center',
                    //sortable: 'custom',
                    minWidth: 110,
                    // 1 -> [0,20],3 -> [20,50], 4 -> [50,100],5 -> [100,200], 6 -> [200,500], 7 -> [500,1000] [1000,2000] ,[2000,4000],[4000,7000],[7000-10000],[10000,20000],[20000,2000000]
                    filters: [{
                        'label': '0-20',
                        'value': '1'
                    }, {
                        'label': '20-50',
                        'value': '2'
                    }, {
                        'label': '50-100',
                        'value': '3'
                    }, {
                        'label': '100-200',
                        'value': '4'
                    }, {
                        'label': '200-500',
                        'value': '5'
                    }, {
                        'label': '500-1000',
                        'value': '6'
                    }, {
                        'label': '1000-2000',
                        'value': '7'
                    }, {
                        'label': '2000-4000',
                        'value': '8'
                    }, {
                        'label': '4000-7000',
                        'value': '9'
                    }, {
                        'label': '7000-10000',
                        'value': '10'
                    }, {
                        'label': '10000-20000',
                        'value': '11'
                    }, {
                        'label': '20000-2000000',
                        'value': '12'
                    }],
                    filterMethod(value, row) {
                        // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                        return row //什么都不做，由专门的函数进行后端筛选
                    },
                    resizable: true,
                    render: (h, params) => {
                        // console.log(params.row)
                        if (!params.row.category) {
                            return h('p', {
                                style: {
                                    'color': 'blue',
                                    'font-weight': 'bold'
                                }
                            }, Math.floor(params.row.baiduIndex * 100) / 100)

                        } else {
                            return h('p', Math.floor(params.row.baiduIndex * 100) / 100)
                        }
                    }
                },

                {
                    title: '状态',
                    key: 'status',
                    align: 'center',
                    minWidth: 120,
                    resizable: true,
                    //filters: [{
                    //    'label': '停止',
                    //    'value': '停止'
                    //}, {
                    //    'label': '无效',
                    //    'value': '无效'
                    //}, {
                    //    'label': '已添加',
                    //    'value': '已添加'
                    //}],
                    //filterMethod(value, row) {
                    //    // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                    //    //if (row.status === value){
                    //    return row //什么都不做，由专门的函数进行后端筛选
                    //    //}
                    //},
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
                        }
                    }
                },
                {
                    title: '分类',
                    key: 'category',
                    align: 'center',
                    minWidth: 120,
                    resizable: true,
                    //filters: [],
                    //filterMultiple: true,
                    //filterMethod(value, row) {
                    //    // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                    //    //if (row.category.includes(value)){
                    //    return row //什么都不做，由专门的函数进行后端筛选
                    //    //}
                    //},
                    render: (h, params) => {
                        if (params.row.category) {
                            return (h('p', params.row.category.join(';')))
                        } else {
                            return (h('p', ''))
                        }

                    }
                },
                {
                    title: '时间',
                    key: 'timestamp',
                    align: 'center',
                    minWidth: 90,
                    resizable: true
                },
                {
                    title: '出处',
                    key: 'source',
                    align: 'center',
                    minWidth: 90,
                    resizable: true,
                },
                {
                    title: '长度',
                    key: 'Length',
                    align: 'center',
                    minWidth: 80,
                    // sortable: 'custom',
                    resizable: true,
                    // filters 对应项目:
                    // 1 -> [0,3], 2 -> [3,5], 3 -> [5,8], 4 -> [8,13],5 -> [13,18], 6 -> [18,25]
                    //filters: [{
                    //    'label': '0-3',
                    //    'value': '1'
                    //}, {
                    //    'label': '3-5',
                    //    'value': '2'
                    //}, {
                    //    'label': '5-8',
                    //    'value': '3'
                    //}, {
                    //    'label': '8-13',
                    //    'value': '4'
                    //}, {
                    //    'label': '13-18',
                    //    'value': '5'
                    //}, {
                    //    'label': '18-25',
                    //    'value': '6'
                    //}],
                    //filterMethod(value, row) {
                    //    // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                    //    return row //什么都不做，由专门的函数进行后端筛选
                    //},
                    render: (h, params) => {
                        // console.log(params.row)
                        return (h('p', params.row.Length)) //.length))
                    }
                },

                {
                    title: '百度备注',
                    key: 'baiduComment',
                    align: 'center',
                    minWidth: 120,
                    resizable: true,
                },
                {
                    title: '用途标签',
                    key: 'usageTag',
                    align: 'center',
                    minWidth: 150,
                    //filters: [],
                    //filterMultiple: true,
                    //filterMethod(value, row) {
                    //    // 现在的筛选策略: 只要是其中 包含 选择项的， 就符合要求
                    //    //if (row.category.includes(value)){
                    //    return row //什么都不做，由专门的函数进行后端筛选
                    //    //}
                    //},
                    resizable: true,
                    render: (h, params) => {
                        let temp = []
                        for (let tag in params.row.usageTag) {
                            temp.push('#' + params.row.usageTag[tag])
                        }
                        return (h('p', temp.join(';')))
                    }
                },
                {
                    title: '操作',
                    key: 'action',
                    slot: 'action',
                    align: 'center',
                    fixed: 'right',
                    minWidth: 160,
                    resizable: true
                }
            ]
        }
    },
    computed: {
        ...mapState(['baseurl', 'currentComponent'])
    },
    components: {
        'i-extendWordItemPage': extendedWordItemPage,
        'i-topoTree': topoTree,
        'i-exportData': exportData,
    },
    mounted() {
        // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize}
        // this.loading = true
        let self = this
        let tagFilter = self.$route.query.tagName
        if (tagFilter) {
            self.usageTagChecked = [tagFilter]
        }
        let Params = {
            'currentPage': self.currentPage,
            'pageSize': self.pageSize,
            'extendedWordItemId': '',
            'wordPart': self.searchItem.toLowerCase(),
            'baiduIndexFilter': encodeURIComponent(self.baiduIndexChecked),
            'bidPriceFilter': encodeURIComponent(self.bidPriceChecked),
            'sortDict': JSON.stringify(self.sortDict),
            'searchCountFilter': encodeURIComponent(self.searchCountChecked),
            'baiduIndexMFilter': encodeURIComponent(self.baiduIndexMChecked),
            'bidPriceMFilter': encodeURIComponent(self.bidPriceMChecked),
            'searchCountMFilter': encodeURIComponent(self.searchCountMChecked)
        }
        //self.fetchMuWords(Params)
        self.fetchInheritWordsES(Params)

        // self.fetchProjectCategories();
        // self.fetchProjectUsageTags()
    },
    methods: {
        ...mapMutations(['changeSearchDisplay']),
        calculateInherit: function () {
            // 到后台，计算母词 统计数据
            let self = this
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'extendedWords/Inherit/jisuan/' + self.currentComponent,
                })
                .then(() => {
                    self.$Message.info('后台正在计算母词统计数据');
                })
                .catch(err => {
                    console.log(err)
                    //self.$Message.error(err.response.data.detail);
                })
        },
        fetchInheritWords: function (prams, applyed = 'all', xindex = 0) {
            //console.log(prams)
            let self = this
            self.tableLoading = true
            // 加上 聚合 的 参数
            // prams['aggGroupBy'] = encodeURIComponent(['mword'])
            return self.axios({
                    method: 'get',
                    url: self.baseurl + 'extendedWords/Inherit/' + self.currentComponent,
                    params: prams
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1
                    self.tableLoading = false
                    if (applyed === 'one') {
                        // 只 获取了单个 母词 统计数据的更新，只更新单个
                        //console.log('one')
                        //self.extendedWordsMuItemData[xindex] = res.data.content[0]
                        res.data.content[0]['id'] = xindex + 1
                        self.$set(self.extendedWordsMuItemData, xindex, res.data.content[0])
                    } else {
                        if (res.data.count !== '') {
                            self.itemMuCount = res.data.count
                        }
                        self.extendedWordsMuItemData = res.data.content
                    }

                    // console.log(self.extendedWordsItemData)
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        fetchInheritWordsES: function (prams, applyed = 'all', xindex = 0) {
            //console.log(prams)
            let self = this
            self.tableLoading = true
            // 加上 聚合 的 参数
            // prams['aggGroupBy'] = encodeURIComponent(['mword'])
            return self.axios({
                    method: 'get',
                    url: self.baseurl + 'extendedWords/Inherit/es/' + self.currentComponent,
                    params: prams
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1
                    self.tableLoading = false
                    if (applyed === 'one') {
                        // 只 获取了单个 母词 统计数据的更新，只更新单个
                        //console.log('one')
                        //self.extendedWordsMuItemData[xindex] = res.data.content[0]
                        res.data.content[0]['id'] = xindex + 1
                        self.$set(self.extendedWordsMuItemData, xindex, res.data.content[0])
                    } else {
                        if (res.data.count !== '') {
                            self.itemMuCount = res.data.count
                        }
                        self.extendedWordsMuItemData = res.data.content
                    }

                    // console.log(self.extendedWordsItemData)
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        handleLoadData: function (item, callback) {
            //console.log(item.word, callback)

            let self = this
            let params = {
                'wordPart': item.word,
                'idPrefix': item.id, //id 用来给 子数据 设置新的id, 新id  =  'id' + '子id'
                'fullMatch': true,
                'currentPage': 0,
                'pageSize': 0,
                'wordItem': 'mword'
            }

            self.axios({
                    method: 'get',
                    url: self.baseurl + 'extendedWords/' + self.currentComponent,
                    params: params
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1
                    //self.tableLoading = false
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    //self.extendedWordsItemData = res.data.content
                    callback(res.data.content)
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })

        },
        setCurrentView: function (select) {
            this.viewSelected = select
            //console.log('this.viewSelected', this.viewSelected)
            if (this.viewSelected === '默认视图') {
                this.$router.push('/Project/' + this.currentComponent + '/extendedWords-bacicView')
            } else if (this.viewSelected === '主题视图') {
                this.$router.push('/Project/' + this.currentComponent + '/extendedWords-topicView')
            } else if (this.viewSelected === '母词视图') {
                this.$router.push('/Project/' + this.currentComponent + '/extendedWords-inheritView')
            }
        },
        onChange: function () {
            let self = this
            // 得到 需要的格式
            let sortDict = {}
            for (let ele in self.sortItems) {
                let lineData = self.sortItems[ele]
                if (lineData.model !== 'default') {
                    sortDict[lineData.id] = lineData.model
                }
            }
            // console.log('sortDict',sortDict)
            self.sortDict = sortDict
            if (Object.keys(sortDict).length !== 0) {
                // 发送排序请求
                self.currentPage = 1
                let Params = {
                    'currentPage': self.currentPage,
                    'pageSize': self.pageSize,
                    'extendedWordItemId': '',
                    'usageTagFilter': encodeURIComponent(self.usageTagChecked),
                    'statusFilter': encodeURIComponent(self.statusChecked),
                    'dataRange': encodeURIComponent(self.dataRange),
                    'wordPart': self.searchItem.toLowerCase(),
                    'categoryFilter': encodeURIComponent(self.categoryChecked),
                    'baiduIndexFilter': encodeURIComponent(self.baiduIndexChecked),
                    'lengthFilter': encodeURIComponent(self.lengthChecked),
                    'bidPriceFilter': encodeURIComponent(self.bidPriceChecked),
                    'sortDict': JSON.stringify(self.sortDict),
                    'searchCountFilter': encodeURIComponent(self.searchCountChecked),
                    'baiduIndexMFilter': encodeURIComponent(self.baiduIndexMChecked),
                    'bidPriceMFilter': encodeURIComponent(self.bidPriceMChecked),
                    'searchCountMFilter': encodeURIComponent(self.searchCountMChecked),
                }
                //    console.log(Params)
                self.fetchInheritWordsES(Params)
            } //else {
            //   self.$Message.info('不排序');
            //}
        },
        seeExpandTree: function (row) {
            let self = this
            // console.log(row.word,index)
            self.topoTreeKeyWord = {
                'kword': row.word,
                'status': '已添加'
            } // 要把状态带上，后端好统一出出力
            // self.topoTreeKey --
            self.topoTreeKey--
            self.topoTreeShow = true
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
            if (Object.keys(sortDict).length !== 0) {
                // 发送排序请求
                self.currentPage = 1
                let Params = {
                    'currentPage': self.currentPage,
                    'pageSize': self.pageSize,
                    'extendedWordItemId': '',
                    'wordPart': self.searchItem.toLowerCase(),
                    'baiduIndexFilter': encodeURIComponent(self.baiduIndexChecked),
                    'bidPriceFilter': encodeURIComponent(self.bidPriceChecked),
                    'sortDict': JSON.stringify(self.sortDict),
                    'searchCountFilter': encodeURIComponent(self.searchCountChecked),
                    'baiduIndexMFilter': encodeURIComponent(self.baiduIndexMChecked),
                    'bidPriceMFilter': encodeURIComponent(self.bidPriceMChecked),
                    'searchCountMFilter': encodeURIComponent(self.searchCountMChecked),
                }
                //    console.log(Params)
                self.fetchInheritWordsES(Params)
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
        singleSearch: function (item) {
            // search item with specifif uid ,so only one will return
            let self = this
            // console.log('item', item)
            //self.searchItem = ''
            //console.log('uid', item['_id']['$oid'])
            //console.log('searchItem', self.searchItem)
            self.searchResult = [] //disapper options window
            self.changeSearchDisplay(item[1])
            // 当进行 single search的时候，因为只关注一条记录，所以，其他筛选项是被忽略的，不发送它们
            self.currentPage = 1
            let Params = {
                'currentPage': 1, //self.currentPage,
                'pageSize': self.pageSize,
                // 'wordPart': item,
                'extendedWordItemId': item[0]
            }
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'UrlId': item['_id']['$oid']}
            //console.log(Params)
            self.fetchInheritWordsES(Params)
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
            self.fetchInheritWordsES(Params)
        },
        extendedWordsSearch: function () {
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
                let Params = {
                    'currentPage': 0,
                    'pageSize': 0,
                    'extendedWordItemId': '',
                    'usageTagFilter': encodeURIComponent(self.usageTagChecked),
                    'statusFilter': encodeURIComponent(self.statusChecked),
                    'dataRange': encodeURIComponent(self.dataRange),
                    'wordPart': self.searchItem.toLowerCase(),
                    'categoryFilter': encodeURIComponent(self.categoryChecked),
                    'baiduIndexFilter': encodeURIComponent(self.baiduIndexChecked),
                    'lengthFilter': encodeURIComponent(self.lengthChecked),
                    'bidPriceFilter': encodeURIComponent(self.bidPriceChecked),
                    'sortDict': JSON.stringify(self.sortDict),
                    'searchCountFilter': encodeURIComponent(self.searchCountChecked),
                    'baiduIndexMFilter': encodeURIComponent(self.baiduIndexMChecked),
                    'bidPriceMFilter': encodeURIComponent(self.bidPriceMChecked),
                    'searchCountMFilter': encodeURIComponent(self.searchCountMChecked),
                }
                // self.fetchItems(Params)
                self.axios({
                        method: 'get',
                        url: self.baseurl + 'extendedWords/' + self.currentComponent,
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
        batchSearch: function (item) {
            // 输入特定查询，按下回车键或 搜索按钮时 ，触发，会返回所有符合条件的项目 或为空
            let self = this
            //console.log('batchSearch')
            //console.log(self.searchItem)
            self.searchResult = []
            self.changeSearchDisplay(item)
            // 下面进行 batchSearch
            self.currentPage = 1
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'dataRange':encodeURIComponent(self.dataRange),'wordPart':self.searchItem.toLowerCase() ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'baiduIndexFilter': encodeURIComponent(self.statusChecked)}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'extendedWordItemId': '',
                'wordPart': item.toLowerCase(), //self.searchItem.toLowerCase(),
                'baiduIndexFilter': encodeURIComponent(self.baiduIndexChecked),
                'bidPriceFilter': encodeURIComponent(self.bidPriceChecked),
                'sortDict': JSON.stringify(self.sortDict),
                'searchCountFilter': encodeURIComponent(self.searchCountChecked),
                'baiduIndexMFilter': encodeURIComponent(self.baiduIndexMChecked),
                'bidPriceMFilter': encodeURIComponent(self.bidPriceMChecked),
                'searchCountMFilter': encodeURIComponent(self.searchCountMChecked),
            }
            // console.log(Params)
            self.fetchInheritWordsES(Params)

        },
        exportDataX: function () {
            let self = this
            // 当没有选项被选中时，默认选中打印当前页
            if (self.selectedItemList.length !== 0) {
                if (self.selectedItemList.length === self.extendedWordsItemData.length) {
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
            self.pageData2Export = self.extendedWordsItemData
            self.expordDataKey++
            self.exportWindowShow = true

        },
        changeExtendedWordStatus: function (id, status) {
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
                    url: self.baseurl + 'extendedWords/' + self.currentComponent + '/' + id,
                    data: myData,
                    params: Params

                })
                .then(res => {
                    // console.log(res)
                    // self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.extendedWordsItemData = res.data.content
                    self.selectedItemList = []
                    return
                    // console.log(self.basicWordsItemData)
                })
                .catch(err => {
                    // console.log(err)
                    self.selectedItemList = []
                    console.log(err.response.data.detail)
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
                        'source': '拓展词'
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
                                            'source': '拓展词',
                                            'exStatus': tempLine['status']
                                        }]
                                        self.axios({
                                                method: 'post',
                                                url: self.baseurl + 'StopDict/',
                                                data: xdata
                                            })
                                            .then(() => {
                                                //console.log('添加到 停止词成功!')

                                                // 然后哦，更改 在拓展词中的状态
                                                self.changeExtendedWordStatus(tempLine['id'], '停止')
                                            })
                                            .catch(err => {
                                                //console.log(err)
                                                self.$Message.error(err.response.data.detail);
                                                self.changeExtendedWordStatus(tempLine['id'], '停止')
                                            })

                                    })
                                    .catch((err) => {
                                        console.log(err);
                                        self.$Message.error("删除失败");
                                    });
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
                                                        'source': '拓展词',
                                                        'exStatus': tempLine['status']
                                                    }]
                                                    self.axios({
                                                            method: 'post',
                                                            url: self.baseurl + 'StopDict/',
                                                            data: xdata
                                                        })
                                                        .then(() => {
                                                            //console.log('添加到 停止词成功!')

                                                            // 然后哦，更改 在拓展词中的状态
                                                            self.changeExtendedWordStatus(tempLine['id'], '停止')
                                                        })
                                                        .catch(err => {
                                                            //console.log(err)
                                                            self.$Message.error(err.response.data.detail);
                                                            self.changeExtendedWordStatus(tempLine['id'], '停止')
                                                        })

                                                })
                                                .catch((err) => {
                                                    console.log(err);
                                                    self.$Message.error("删除失败");
                                                });
                                        } else {
                                            // 不存在于用户词典中
                                            // 那么，接下来直接往 停止词典里面插入，不管存不存在，如果存在，会自动报错跳过
                                            // 然后，将该词添加到 停止词
                                            let xdata = [{
                                                'word': tempLine['word'],
                                                'operator': localStorage.getItem('kwmUser'),
                                                'source': '拓展词',
                                                'exStatus': tempLine['status']
                                            }]
                                            self.axios({
                                                    method: 'post',
                                                    url: self.baseurl + 'StopDict/',
                                                    data: xdata
                                                })
                                                .then(() => {
                                                    //console.log('添加到 停止词成功!')

                                                    // 然后哦，更改 在拓展词中的状态
                                                    self.changeExtendedWordStatus(tempLine['id'], '停止')
                                                })
                                                .catch(err => {
                                                    //console.log(err)
                                                    self.$Message.error(err.response.data.detail);
                                                    self.changeExtendedWordStatus(tempLine['id'], '停止')
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
                        'source': '拓展词'
                    }
                    //console.log('tempLine', tempLine)

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
                                            'source': '拓展词',
                                            'exStatus': tempLine['status']
                                        }]
                                        self.axios({
                                                method: 'post',
                                                url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                                                data: xdata
                                            })
                                            .then(() => {
                                                //console.log('添加到 无效词成功!')

                                                // 然后哦，更改 在拓展词中的状态
                                                self.changeExtendedWordStatus(tempLine['id'], '无效')
                                            })
                                            .catch(err => {
                                                //console.log(err)
                                                self.$Message.error(err.response.data.detail);
                                                self.changeExtendedWordStatus(tempLine['id'], '无效')
                                            })

                                    })
                                    .catch((err) => {
                                        console.log(err);
                                        self.$Message.error("删除失败");
                                    });
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
                                                        'source': '拓展词',
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
                                                            self.changeExtendedWordStatus(tempLine['id'], '无效')
                                                        })
                                                        .catch(err => {
                                                            //console.log(err)
                                                            self.$Message.error(err.response.data.detail);
                                                            self.changeExtendedWordStatus(tempLine['id'], '无效')
                                                        })

                                                })
                                                .catch((err) => {
                                                    console.log(err);
                                                    self.$Message.error("删除失败");
                                                });
                                        } else {
                                            // 不存在于用户词典中
                                            // 那么，接下来直接往 无效词典里面插入，不管存不存在，如果存在，会自动报错跳过
                                            // 然后，将该词添加到 无效词
                                            //console.log('不存在于 用户词典中')
                                            let xdata = [{
                                                'word': tempLine['word'],
                                                'operator': localStorage.getItem('kwmUser'),
                                                'source': '拓展词',
                                                'exStatus': tempLine['status']
                                            }]
                                            self.axios({
                                                    method: 'post',
                                                    url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                                                    data: xdata
                                                })
                                                .then(() => {
                                                    //console.log('添加到 无效词成功!')

                                                    // 然后哦，更改 在拓展词中的状态
                                                    self.changeExtendedWordStatus(tempLine['id'], '无效')
                                                })
                                                .catch(err => {
                                                    //console.log(err)
                                                    self.$Message.error(err.response.data.detail);
                                                    self.changeExtendedWordStatus(tempLine['id'], '无效')
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
        handleUpdateExtendedWordItem: function (data2Update) {
            let self = this

            let pageParams = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            //console.log('mmm', pageParams, data2Update.data)
            let idx = data2Update.data['id']
            delete data2Update.data['id']
            self.axios({
                    method: 'patch',
                    url: self.baseurl + 'extendedWords/' + self.currentComponent + '/' + data2Update.uid,
                    data: data2Update.data,
                    params: pageParams
                })
                .then(() => {

                    let target = ''
                    let xid = ''
                    let xindex = ''
                    for (let ele in self.extendedWordsMuItemData) {
                        let lineData = self.extendedWordsMuItemData[ele]
                        if (lineData['id'] === parseInt(idx.split('-')[0])) {
                            target = lineData['word']
                            xid = lineData['id']
                            xindex = ele
                            break
                        }
                    }

                    let params = {
                        'wordPart': target,
                        'idPrefix': xid, //id 用来给 子数据 设置新的id, 新id  =  'id' + '子id'
                        'fullMatch': true,
                        'currentPage': 0,
                        'pageSize': 0,
                        'wordItem': 'mword'
                    }

                    self.axios({
                            method: 'get',
                            url: self.baseurl + 'extendedWords/' + self.currentComponent,
                            params: params
                        })
                        .then(res => {
                            //console.log('bbbb', res)
                            // self.currentPage = 1
                            //self.tableLoading = false
                            if (res.data.count !== '') {
                                self.itemCount = res.data.count
                            }
                            //self.extendedWordsItemData = res.data.content
                            self.$set(self.extendedWordsMuItemData[xindex], 'children', res.data.content)
                            // console.log(self.extendedWordsItemData)

                            // 现在拉取 当前 母词 更新
                            let params = {
                                'currentPage': 0,
                                'pageSize': 0,
                                'wordPart': target,
                            }
                            self.fetchInheritWords(params, 'one', parseInt(xid - 1))
                        })
                        .catch(err => {
                            console.log(err)
                        })

                })
                .catch(err => {
                    // console.log(err)
                    console.log(err.response.data.detail)
                    self.$Message.error(err.response.data.detail);
                })
        },
        handledeleteExtendedWordItem: function (uids) {
            let self = this

            let myIds = new Set()
            for (let ele in uids) {
                myIds.add(parseInt(uids[ele]['id'].split('-')[0]))
                delete uids[ele]['id']
            }
            myIds = Array.from(myIds) // 去重
            //console.log(myIds, uids)
            // 联系后台，进行删除
            self.axios({
                    method: 'delete',
                    url: self.baseurl + 'extendedWords/' + self.currentComponent,
                    data: uids
                })
                .then(() => {

                    // 先更新 总的 条目
                    let Params = {
                        'currentPage': self.currentPage,
                        'pageSize': self.pageSize
                    }
                    self.fetchMuWords(Params)

                    // 然后，在更新每一个 单独条目下 的 子 元素
                    // 循环更新每一个 主题词 集合
                    for (let ele in myIds) {
                        let myid = myIds[ele]
                        //console.log('myid=', myid)
                        let target = ''
                        let xindex = ''
                        for (let ele in self.extendedWordsMuItemData) {
                            let lineData = self.extendedWordsMuItemData[ele]
                            if (lineData['id'] === myid) {
                                target = lineData['word']
                                xindex = ele
                                break
                            }
                        }

                        let params = {
                            'wordPart': target,
                            'idPrefix': myid, //id 用来给 子数据 设置新的id, 新id  =  'id' + '子id'
                            'fullMatch': true,
                            'currentPage': 0,
                            'pageSize': 0,
                            'wordItem': 'mword'
                        }
                        //console.log('params', params)
                        self.axios({
                                method: 'get',
                                url: self.baseurl + 'extendedWords/' + self.currentComponent,
                                params: params
                            })
                            .then(res => {
                                //console.log('xres', res)
                                // self.currentPage = 1
                                //self.tableLoading = false
                                if (res.data.count !== '') {
                                    self.itemCount = res.data.count
                                }
                                //self.extendedWordsItemData = res.data.content
                                self.$set(self.extendedWordsMuItemData[xindex], 'children', res.data.count)
                                // console.log(self.extendedWordsItemData)
                            })
                            .catch(err => {
                                console.log(err)
                            })
                    }
                })
                .catch(err => {
                    // console.log(err)
                    console.log(err.response.data.detail)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        editItem: function (row) {
            let self = this
            self.formCustom = {}
            self.$set(self.formCustom, 'uid', row['_id']['$oid'])
            self.$set(self.formCustom, 'Items', [{
                'existed': '已存在',
                'status': row.status,
                'id': row.id,
                // 'index': index + 1,
                'word': row.word,
                'category': row.category,
                'mword': row.mword,
                'topicWord': row.topicWord,
                'baiduIndex': row.baiduIndex,
                'searchCount': row.searchCount,
                'bidPrice': row.bidPrice,
                'baiduIndexM': row.baiduIndexM,
                'searchCountM': row.searchCountM,
                'bidPriceM': row.bidPriceM,
                'usageTag': row.usageTag,
                'baiduComment': row.baiduComment
            }])
            self.refreshFlag--
            self.extendedWordItemShow = true
        },
        seeNearWords: function () {
            console.log('xx')
        },
        handleSelectRow: function () {
            this.selectedItemList = this.$refs.table.getSelection()
        },
        createExtendedWords: function (data2Create) {
            // console.log(data2Create)
            let self = this
            self.currentPage = Math.ceil((self.itemCount + 1) / self.pageSize)
            let pageParams = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            self.axios({
                    method: 'post',
                    url: self.baseurl + 'extendedWords/' + self.currentComponent,
                    data: data2Create,
                    params: pageParams
                })
                .then(res => {
                    // console.log(res)
                    // self.currentPage = 1
                    if (res.data.count !== '') {
                        self.itemCount = res.data.count
                    }
                    self.extendedWordsItemData = res.data.content
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
        fetchProjectUsageTags: function () {
            // 获取该项目中，extendedWords表中 定义的所有 usage tags
            let self = this
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'extendedWords/usageTag/' + self.currentComponent
                })
                .then(res => {
                    // console.log(res)
                    self.projetcUsageTagsList = [] // 先初始化
                    for (let ele in res.data.content) {
                        self.projetcUsageTagsList.push({
                            'label': res.data.content[ele],
                            'value': res.data.content[ele]
                        })
                    }
                    // console.log(self.projetcUsageTagsList)
                    self.columns1[15].filters = self.projetcUsageTagsList // 必须要设置一下 ，
                    // console.log(self.rawCategories)
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
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
                    self.columns1[10].filters = self.projetcCategoriesList // 必须要设置一下 ，目录列表
                    // console.log(self.rawCategories)
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        fetchMuWordsES: function (prams) {
            //console.log(prams)
            let self = this
            self.tableLoading = true
            // 加上 聚合 的 参数
            //prams['aggGroupBy'] = encodeURIComponent(['topicWord'])
            // 加上排序的参数

            // let pageParams = {
            //     'currentPage': self.currentPage,
            //     'pageSize': self.pageSize,
            //     'aggGroupBy': encodeURIComponent(['topicWord']),
            // }
            //console.log('prams44', prams)
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'extendedWords/Muci/es/' + self.currentComponent,
                    params: prams
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1
                    self.tableLoading = false
                    if (res.data.count !== '') {
                        self.itemMuCount = res.data.count
                    }
                    //self.extendedWordsItemData = res.data.content
                    self.extendedWordsMuItemData = res.data.content
                    // console.log(self.extendedWordsItemData)
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        fetchMuWords: function (prams) {
            //console.log(prams)
            let self = this
            self.tableLoading = true
            // 加上 聚合 的 参数
            //prams['aggGroupBy'] = encodeURIComponent(['topicWord'])
            // 加上排序的参数

            // let pageParams = {
            //     'currentPage': self.currentPage,
            //     'pageSize': self.pageSize,
            //     'aggGroupBy': encodeURIComponent(['topicWord']),
            // }
            //console.log('prams44', prams)
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'extendedWords/Muci/' + self.currentComponent,
                    params: prams
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1
                    self.tableLoading = false
                    if (res.data.count !== '') {
                        self.itemMuCount = res.data.count
                    }
                    //self.extendedWordsItemData = res.data.content
                    self.extendedWordsMuItemData = res.data.content
                    // console.log(self.extendedWordsItemData)
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
                    url: self.baseurl + 'extendedWords/es/' + self.currentComponent,
                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1
                    self.tableLoading = false
                    if (res.data.count !== '') {
                        self.itemMuCount = res.data.count
                    }
                    self.extendedWordsMuItemData = res.data.content
                    // console.log(self.extendedWordsItemData)
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
                    url: self.baseurl + 'extendedWords/' + self.currentComponent,
                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    // self.currentPage = 1
                    self.tableLoading = false
                    if (res.data.count !== '') {
                        self.itemMuCount = res.data.count
                    }
                    self.extendedWordsMuItemData = res.data.content
                    // console.log(self.extendedWordsItemData)
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
            // console.log('checked',chekced)
            if (chekced.key === 'category') {
                self.categoryChecked = chekced['checked']
            } else if (chekced.key === 'status') {
                self.statusChecked = chekced['checked']
            } else if (chekced.key === 'Length') {
                self.lengthChecked = chekced['checked']
            } else if (chekced.key === 'baiduIndex') {
                self.baiduIndexChecked = chekced['checked']
            } else if (chekced.key === 'searchCount') {
                self.searchCountChecked = chekced['checked']
            } else if (chekced.key === 'bidPrice') {
                self.bidPriceChecked = chekced['checked']
            } else if (chekced.key === 'usageTag') {
                self.usageTagChecked = chekced['checked']
            } else if (chekced.key === 'baiduIndexM') {
                self.baiduIndexMChecked = chekced['checked']
            } else if (chekced.key === 'searchCountM') {
                self.searchCountMChecked = chekced['checked']
            } else if (chekced.key === 'bidPriceM') {
                self.bidPriceMChecked = chekced['checked']
            }

            // console.log( self.statusChecked, self.categoryChecked)

            //重新筛选，激发重新搜索  ，包含 状态 和 分类. 此时 包含的查询参数  必须有: currentPage, pageSize, 可能有: urlPart,categoryFilter ,baiduIndexFilter

            self.currentPage = 1
            // let Params = {'currentPage':self.currentPage,'pageSize':self.pageSize,'dataRange':encodeURIComponent(self.dataRange),'urlPart':self.searchItem.toLowerCase() ,'categoryFilter': encodeURIComponent(self.categoryChecked), 'baiduIndexFilter': encodeURIComponent(self.statusChecked)}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'extendedWordItemId': '',
                'wordPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'baiduIndexFilter': encodeURIComponent(self.baiduIndexChecked),
                'bidPriceFilter': encodeURIComponent(self.bidPriceChecked),
                'sortDict': JSON.stringify(self.sortDict),
                'searchCountFilter': encodeURIComponent(self.searchCountChecked),
                'baiduIndexMFilter': encodeURIComponent(self.baiduIndexMChecked),
                'bidPriceMFilter': encodeURIComponent(self.bidPriceMChecked),
                'searchCountMFilter': encodeURIComponent(self.searchCountMChecked),
            }
            self.fetchInheritWordsES(Params)

        },
        pageChange: function (pageIndex) {
            // console.log(pageIndex)
            let self = this

            self.currentPage = pageIndex
            // let Params = {'currentPage':this.currentPage,'pageSize':this.pageSize}
            let Params = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize,
                'extendedWordItemId': '',
                'wordPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'baiduIndexFilter': encodeURIComponent(self.baiduIndexChecked),
                'bidPriceFilter': encodeURIComponent(self.bidPriceChecked),
                'sortDict': JSON.stringify(self.sortDict),
                'searchCountFilter': encodeURIComponent(self.searchCountChecked),
                'baiduIndexMFilter': encodeURIComponent(self.baiduIndexMChecked),
                'bidPriceMFilter': encodeURIComponent(self.bidPriceMChecked),
                'searchCountMFilter': encodeURIComponent(self.searchCountMChecked),
            }
            self.fetchInheritWordsES(Params)

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
                'extendedWordItemId': '',
                'usageTagFilter': encodeURIComponent(self.usageTagChecked),
                'statusFilter': encodeURIComponent(self.statusChecked),
                'dataRange': encodeURIComponent(self.dataRange),
                'wordPart': self.searchItem.toLowerCase(),
                'categoryFilter': encodeURIComponent(self.categoryChecked),
                'baiduIndexFilter': encodeURIComponent(self.baiduIndexChecked),
                'lengthFilter': encodeURIComponent(self.lengthChecked),
                'bidPriceFilter': encodeURIComponent(self.bidPriceChecked),
                'sortDict': JSON.stringify(self.sortDict),
                'searchCountFilter': encodeURIComponent(self.searchCountChecked),
                'baiduIndexMFilter': encodeURIComponent(self.baiduIndexMChecked),
                'bidPriceMFilter': encodeURIComponent(self.bidPriceMChecked),
                'searchCountMFilter': encodeURIComponent(self.searchCountMChecked),
            }
            self.fetchInheritWords(Params)

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
            // 当没有选项被选中时，不进行该操作
            let uids = []
            //console.log('self.selectedItemList', self.selectedItemList)
            for (let element in self.selectedItemList) {
                let mword = ''
                if (self.selectedItemList[element]['mword']) {
                    mword = self.selectedItemList[element]['mword']
                }
                uids.push({
                    'uid': self.selectedItemList[element]['_id']['$oid'],
                    'mword': mword,
                    'id': self.selectedItemList[element]['id']
                })
            }
            //console.log(uids)
            self.handledeleteExtendedWordItem(uids)
        },
        addItem: function () {
            let self = this
            self.formCustom = {
                    //itemIndex: 1,
                    uid: '',
                    Items: [{
                        //index: 1,
                        status: '已添加',
                        existed: '状态',
                        word: '',
                        category: [],
                        mword: '',
                        topicWord: '',
                        baiduIndex: '',
                        searchCount: '',
                        bidPrice: '',
                        baiduIndexM: '',
                        searchCountM: '',
                        bidPriceM: '',
                        baiduComment: '',
                        usageTag: []
                    }]
                },
                self.refreshFlag--
            self.extendedWordItemShow = true
        }
    }
}
</script>

<style scoped>
>>>.ivu-table-cell {
    padding: 5px !important
}

.basicWord-batchUpload {
    border: 1px solid green;
    border-radius: 5px;
    width: 140px
}

.basicWord-batchUpload-button {
    padding: 5px;
}

.basicWord-batchUpload-template {
    border-top: 1px solid green;
    padding: 3px
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
    width: 980px;
    border-radius: 5px;
    margin-left: -5px
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

.xx1 {
    flex: 7;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    justify-content: space-between
}

.xx3,
.xx2 {
    fles: 1;
    flex-wrap: wrap;
    margin-left: 5px;
    margin-right: 10px
}

.p2 {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px
}

.p21 {
    display: flex;
    justify-content: space-between;
    align-items: center
}

.page {
    margin-left: 5px;
}

.ivu-radio-group-button .ivu-radio-wrapper-checked {
    background-color: #212891;
    color: #fff
}

.p11 {
    display: flex;
    align-items: center;
    justify-content: space-between
}

.page {
    margin-left: 50px;
    margin-right: 50px
}

.calculate {
    margin-left: 25px
}
</style>
