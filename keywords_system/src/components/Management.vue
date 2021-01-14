<template>
<div class="Management">
    <div class="Management-tools">
        <i-page :total="projectCount" placement="bottom" :current="currentPage" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />
        <createNewproject class="Management-tools-create" @createNeWProject="handleNewProject"></createNewproject>
    </div>
    <div v-if="showLoading" class="demo-spin-col" span="8">
        <i-spin fix>
            <i-icon type="ios-loading" size=18 class="demo-spin-icon-load"></i-icon>
            <div>Loading</div>
        </i-spin>
    </div>

    <div v-else class="Management-cards">
        <i-card class="Management-card" style="width:300px" v-for="(rowData,index) in projectLists" :key="index">
            <div class="Management-card-in">
                <div class="Management-input-project-name">
                    <div>
                        <i-form ref="normalFormProject" :model="normalFormProject" :rules="normalRules" v-if="editIndexProject === index">
                            <i-formItem prop="editProject">
                                <i-input type="text" v-model="normalFormProject.editProject" />
                            </i-formItem>
                        </i-form>
                        <div class="Management-input-project-title" v-else>
                            <span class="middle"> {{rowData.id}}</span>
                            <i-icon type="ios-film"></i-icon>
                            <router-link class="Management-input-project-title-main" :to="'/Project/'+(rowData.projectName)">{{ rowData.projectName }}</router-link>
                        </div>
                    </div>

                    <div>
                        <div v-if="editIndexProject === index" class="Management-input-project-title-change">
                            <i-button class="Management-input-project-normal" @click="handleSave(rowData,'project',index,normalFormProject.editProject)" size="small" type="success">保存</i-button>
                            <i-button class="Management-input-project-normal" @click="handleCancle(rowData)" size="small">取消</i-button>
                            <i-button class="Management-input-project-normal Management-input-project-delete" @click="handleDelete(rowData,'project',index,normalFormProject.editProject)" size="small" type="error">删除</i-button>
                        </div>
                        <div v-else>
                            <i-button class="Management-input-project-name-midify" @click="handleEditProject(rowData, index)" size="small">修改项目</i-button>
                        </div>

                    </div>
                </div>
            </div>
            <div class="Management-input-project-categories">
                <div class="Management-input-category-item" v-for="(category, innerIndex) in rowData.categories" :key="innerIndex">

                    <i-form ref="normalFormCategory" :model="normalFormCategory" :rules="normalRules" v-if="EditIndexcategory === index + '-' + innerIndex">
                        <i-formItem prop="editCategory">
                            <i-input type="text" v-model="normalFormCategory.editCategory" />
                        </i-formItem>
                    </i-form>
                    <span class="categoryName-collpse" title="双击可编辑" v-else @dblclick="handleEditCategory(rowData,index,innerIndex)">{{ category.categoryName}}</span>
                    <i-button v-if="EditIndexcategory === index + '-' + innerIndex" class="Management-input-project-normal " @click="handleSave(rowData,'categories',innerIndex,normalFormCategory.editCategory)" size="small" type="success">保存</i-button>
                    <i-button v-if="EditIndexcategory === index + '-' + innerIndex" class="Management-input-project-normal " @click="handleCancle(rowData)" size="small">取消</i-button>
                    <i-button v-if="EditIndexcategory === index + '-' + innerIndex" class="Management-input-project-normal Management-input-project-delete" @click="handleDelete(rowData,'categories',innerIndex)" size="small" type="error">删除</i-button>
                </div>
                <i-button type="dashed" icon="md-add" @click="addCategory(rowData,index)" :disabled="createCategoryBottonStatus">创建分类</i-button>
            </div>

            <div class="Management-cards-footer">
                <p>用户</p>
                <a class="Management-cards-footer-creater" :href="'mailto:' + rowData.creater">{{rowData.creater|getName}}</a>
                <p>创建于</p>
                <p class="Management-cards-footer-timestamp">{{rowData.timestamp}}</p>
            </div>
        </i-card>
    </div>
    <i-page :total="projectCount" :current="currentPage" placement="top" :page-size="pageSize" :page-size-opts=[10,20,30,40,50,100] size="small" show-elevator show-total show-sizer @on-change="pageChange" @on-page-size-change="pageSizeChange" />

    <!-- loading-->

    

</div>
</template>

<script>
import {
    mapState,
    mapMutations
} from 'vuex'
import createNewproject from '@/components/Management/createNewproject.vue'
export default {
    name: 'projectScope',
    data() {
        const validateProject = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('该项不能为空'));
            } else if (value.indexOf(" ") != -1 || value.indexOf("'") != -1 || value.indexOf('"') != -1 || value.indexOf('/') != -1) {
                callback(new Error("项目名称不能包含空格,\",','/'"));
            } else if (value.length >= 250) {
                callback(new Error("长度不能超过250个字符!"));
            } else {
                callback();
            }
        };
        return {
            showLoading: true,
            projectCount: 0, // 分页中项目总数
            currentPage: 1,
            pageSize: 10,
            newCategotyFlag: false, // if the category edited is just created thathas not synced to backend
            createCategoryBottonStatus: false,
            normalFormProject: {
                editProject: '', // 第一列输入框，当然聚焦的输入框的输入内容，与 data 分离避免重构的闪烁
            },
            normalFormCategory: {
                editCategory: ''
            },
            normalRules: {
                editProject: [{
                    validator: validateProject,
                    trigger: 'blur'
                }],
                editCategory: [{
                    validator: validateProject,
                    trigger: 'blur'
                }]
            },
            editIndexProject: -1, // 当前聚焦的输入框的行数
            EditIndexcategory: -1,
            //editProject: '',  // 第一列输入框，当然聚焦的输入框的输入内容，与 data 分离避免重构的闪烁
            //editCategory: '',
            projectLists: ''
        }
    },
    computed: {
        ...mapState(['baseurl'])
    },
    filters: {
        getName: function (value) {
            if (!value) return ''
            value = value.toString()
            return value.split('@')[0]
        }
    },
    components: {
        'createNewproject': createNewproject
    },
    created() {
        this.changeCurrentComponent('项目管理')
        // 获取所有项目数据
        this.fetchAllProjects()

    },
    beforeDestroy() {
        this.$Message.destroy()
    },
    methods: {
        ...mapMutations(['changeCurrentComponent']),
        handleEditProject: function (row, index) {
            this.normalFormProject.editProject = row.projectName;
            this.editIndexProject = index;
            this.createCategoryBottonStatus = true
        },
        handleCancle: function (xrow) {
            // 首先处理 新建分类的情形
            if (this.newCategotyFlag) {
                this.newCategotyFlag = false
                xrow.categories.pop()
                this.normalFormCategory.editCategory = ''
            }
            this.editIndexProject = -1
            this.EditIndexcategory = -1
            this.normalFormProject.editProject = ''
            this.normalFormCategory.editCategory = ''
            this.createCategoryBottonStatus = false
        },
        handleDelete: function (xrow, xtype, xindex) {
            //console.log(xrow,xtype,xindex)
            let self = this
            if (xtype === 'project') {
                // 删除项目
                let projectId = xrow['_id']['$oid']
                let pageParams = {
                    'currentPage': self.currentPage,
                    'pageSize': self.pageSize
                }
                self.axios({
                        method: 'delete',
                        url: self.baseurl + 'Projects/' + projectId,
                        params: pageParams
                    })
                    .then(res => {
                        // console.log(res)
                        // 成功后会自动拉去所有最新数据，重新渲染页面

                        if (res.data.count !== '') {
                            self.projectCount = res.data.count
                        }
                        self.projectLists = res.data.content
                    })
                    .catch(() => {
                        //console.log(err)
                        // self.$Message.error(err.response.data.detail);
                    })
                //this.projectLists.splice(xindex,1)
            } else if (xtype === 'categories') {
                // 首先处理 新建分类的情形
                if (self.newCategotyFlag) {
                    self.newCategotyFlag = false
                    //console.log(xrow.categories.length)
                    xrow.categories.pop()
                    //console.log(xrow.categories.length)
                    self.normalFormCategory.editCategory = ''
                } else {
                    let categoryId = xrow.categories[xindex]['_id']['$oid']
                    let projectId = xrow['_id']['$oid']
                    let pageParams = {
                        'currentPage': self.currentPage,
                        'pageSize': self.pageSize
                    }
                    self.axios({
                            method: 'delete',
                            url: self.baseurl + 'Categories/' + projectId + '/' + categoryId,
                            params: pageParams
                        })
                        .then(res => {
                            // console.log(res)
                            // 成功后会自动拉去所有最新数据，重新渲染页面
                            if (res.data.count !== '') {
                                self.projectCount = res.data.count
                            }
                            self.projectLists = res.data.content
                        })
                        .catch(() => {
                            //console.log(err)
                            // self.$Message.error(err.response.data.detail);
                        })
                }
            }
            // self.currentPage = 1
            self.editIndexProject = -1
            self.EditIndexcategory = -1
            self.createCategoryBottonStatus = false
        },
        ifChanged: function (before, after) {
            // 本函数用来检查 字段是否被更改，只有被更改过的字段才会发起后台同步请求
            if (before === after) {
                return false
            } else {
                return true
            }
        },
        handleSave: function (xrow, xtype, xindex, xvalue) {
            //console.log (xrow,xtype,xindex,xvalue)
            let self = this
            if (xtype === 'project') {
                self.$refs['normalFormProject'][0].validate((valid) => { // 此处要加[0]，这是一个bug
                    if (valid) {
                        console.log('验证成功')
                        //保存项目
                        // 如果字段确实被改了，才同步，否则， 相当于点击了取消
                        if (self.ifChanged(xrow.projectName, xvalue)) {
                            //xrow.projectName = xvalue
                            //console.log('出现改变，进行同步更新')
                            let projectId = xrow['_id']['$oid']
                            let payLoad = {
                                'projectName': xvalue
                            }
                            // let payLoad = {'projectName':self.normalFormProject.editProject }
                            // 进行同步
                            let pageParams = {
                                'currentPage': self.currentPage,
                                'pageSize': self.pageSize
                            }
                            self.axios({
                                    method: 'patch',
                                    url: self.baseurl + 'Projects/' + projectId,
                                    data: payLoad,
                                    params: pageParams
                                })
                                .then(res => {
                                    // console.log(res)
                                    if (res.data.count !== '') {
                                        self.projectCount = res.data.count
                                    }
                                    self.projectLists = res.data.content
                                })
                                .catch(err => {
                                    //console.log(err)
                                    self.$Message.error({
                                        content: JSON.stringify(err.response.data.detail),
                                        duration: 0,
                                        closable: true
                                    });

                                })
                        } else {
                            //console.log('没有被修改，什么也不做')
                            self.$refs['normalFormProject'][0].resetFields()
                        }
                        self.EditIndexcategory = -1
                        self.editIndexProject = -1
                        self.createCategoryBottonStatus = false
                    } else {
                        console.log('验证失败')
                        self.createCategoryBottonStatus = false
                    }
                })
            } else if (xtype === 'categories') {
                self.$refs['normalFormCategory'][0].validate((valid) => {
                    if (valid) {
                        console.log('验证成功')
                        // 首先处理 新建分类的情形
                        if (self.newCategotyFlag) {
                            self.newCategotyFlag = false
                            // 同步到 后端
                            let projectId = xrow['_id']['$oid']
                            let payLoad = {
                                'categoryName': self.normalFormCategory.editCategory
                            }
                            let pageParams = {
                                'currentPage': self.currentPage,
                                'pageSize': self.pageSize
                            }
                            self.axios({
                                    method: 'post',
                                    url: self.baseurl + 'Categories/' + projectId,
                                    params: pageParams,
                                    data: payLoad
                                })
                                .then(res => {
                                    // console.log(res)
                                    // 成功后会自动拉去所有最新数据，重新渲染页面
                                    if (res.data.count !== '') {
                                        self.projectCount = res.data.count
                                    }
                                    self.projectLists = res.data.content
                                })
                                .catch(err => {
                                    //console.log(err)
                                    xrow.categories.pop()
                                    self.newCategotyFlag = false
                                    //self.$Message.error(err.response.data.detail);
                                    self.$Message.error({
                                        content: JSON.stringify(err.response.data.detail),
                                        duration: 0,
                                        closable: true
                                    });
                                })
                            self.normalFormCategory.editCategory = ''
                        } else {
                            // 只有字段被修改，才同步到服务端
                            if (self.ifChanged(xrow.categories[xindex].categoryName, xvalue)) {
                                //保存目录
                                //console.log('出现更改')
                                // 进行同步
                                //console.log(xvalue)
                                let categoryId = xrow.categories[xindex]['_id']['$oid']
                                let projectId = xrow['_id']['$oid']
                                let payLoad = {
                                    'categoryName': xvalue
                                }
                                let pageParams = {
                                    'currentPage': self.currentPage,
                                    'pageSize': self.pageSize
                                }
                                self.axios({
                                        method: 'patch',
                                        url: self.baseurl + 'Categories/' + projectId + '/' + categoryId,
                                        params: pageParams,
                                        data: payLoad
                                    })
                                    .then(res => {
                                        // console.log(res)
                                        // 成功后会自动拉去所有最新数据，重新渲染页面
                                        if (res.data.count !== '') {
                                            self.projectCount = res.data.count
                                        }
                                        self.projectLists = res.data.content
                                    })
                                    .catch(err => {
                                        //console.log(err)
                                        //self.$Message.error(err.response.data.detail);
                                        self.$Message.error({
                                            content: JSON.stringify(err.response.data.detail),
                                            duration: 0,
                                            closable: true
                                        });
                                    })
                            } else {
                                //console.log('没有更改')
                                self.$refs['normalFormCategory'][0].resetFields()
                            }
                        }
                        self.EditIndexcategory = -1
                        self.editIndexProject = -1
                        self.createCategoryBottonStatus = false
                    } else {
                        console.log('验证失败')
                        self.createCategoryBottonStatus = false
                    }
                })
            }
        },
        handleEditCategory: function (row, index, InnerIndex) {
            this.normalFormCategory.editCategory = row.categories[InnerIndex].categoryName;
            this.EditIndexcategory = index + '-' + InnerIndex;
            // console.log(this.EditIndexcategory,this.normalFormCategory.editCategory)
        },
        // EditIndexcategory === index + '-' + innerIndex
        addCategory: function (xrow, xindex) {
            xrow.categories.push({
                'categoryName': '默认值'
            })
            this.newCategotyFlag = true
            this.normalFormCategory.editCategory = '默认值'
            let currentIndex = xrow.categories.length - 1
            this.EditIndexcategory = xindex + '-' + currentIndex
            this.createCategoryBottonStatus = true
        },
        handleNewProject: function (projectData) {
            let self = this
            let pageParams = {
                'currentPage': Math.ceil((self.projectCount + 1) / self.pageSize), //去到最后一页
                'pageSize': self.pageSize
            }
            self.axios({
                    method: 'post',
                    url: self.baseurl + 'Projects/',
                    params: pageParams,
                    data: projectData
                })
                .then(res => {
                    // console.log(res)
                    if (res.data.count !== '') {
                        self.projectCount = res.data.count
                    }
                    self.projectLists = res.data.content
                })
                .catch(err => {
                    //console.log(err)
                    //self.$Message.error(err.response.data.detail);
                    self.$Message.error({
                        content: JSON.stringify(err.response.data.detail),
                        duration: 0,
                        closable: true
                    });
                })
        },
        fetchAllProjects: function () {
            let self = this
            self.showLoading = true
            let pageParams = {
                'currentPage': self.currentPage,
                'pageSize': self.pageSize
            }
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Projects/',
                    params: pageParams
                })
                .then(res => {
                    //console.log(res)
                    if (res.data.count !== '') {
                        self.projectCount = res.data.count
                    }
                    self.showLoading = false
                    self.projectLists = res.data.content

                })
                .catch(() => {
                    self.showLoading = false
                    //console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        pageChange: function (pageIndex) {
            // console.log(pageIndex)
            this.currentPage = pageIndex
            this.fetchAllProjects()
        },
        pageSizeChange: function (pageSize) {
            this.pageSize = pageSize
            this.currentPage = 1
            // console.log(pageSize)
            this.fetchAllProjects()
        }
    },
    props: {}
}
</script>

<style scoped>
.Management {
    margin: 20px 50px
}

.Management-tools {
    display: flex;
    justify-content: center;
    align-items: center
}

.Management-tools-create {
    margin-left: 20px
}

.Management-cards {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    flex-wrap: wrap;
    margin: 10px 5px;
    background-color: #F4F7F9;
    min-height: 550px
}

.Management-card {
    margin: 10px 10px;
    min-height: 210px
}

.Management-card-in {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-content: space-around
}

.Management-input-project-name {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin: 0px 10px
}

.Management-cards-footer {
    display: flex;
    font-size: 0.9rem;
    justify-content: center;
    align-items: flex-end
}

.Management-cards-footer-creater {
    margin: auto 5px;
    font-weight: bold;
    max-width: 60px;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow-x: auto
}

.Management-cards-footer-timestamp {
    margin: auto 5px;
    font-weight: bold;
    font-style: italic
}

.Management-input-project-categories {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    flex-wrap: wrap;
    align-content: flex-start;
    height: 150px;
    overflow: auto;
    border-top: 1px solid #DBDEE2;
    border-bottom: 1px solid #DBDEE2;
    margin: 5px 0;
    padding: 5px;

}

.Management-input-project-title-change {
    display: flex
}

.Management-input-project {
    display: flex;
    align-items: center
}

.Management-input-project-title {
    width: 200px;
    font-size: 1.1rem;
    font-weight: bold;
    overflow: auto;
    text-overflow: ellipsis;
    white-space: nowrap;
    text-align: left
}

.Management-input-project-title-main {
    color: #212891
}

.Management-input-project-action {
    margin-left: 10px
}

.Management-input-project-normal {
    margin-left: 3px
}

.Management-input-project-delete {
    margin-left: 10px
}

.Management-input-category {
    display: flex;
    flex-wrap: wrap;
    align-items: center
}

.Management-input-category-item {
    border: 1px solid #bdbbbb;
    margin: 5px;
    border-radius: 3px;
    padding: 3px 3px;
    z-index: 5;
    background-color: #F4F7F9
}

.categoryName-collpse {
    max-width: 50px;
    overflow: auto;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.Management-input-category-item:hover {
    box-shadow: 0 1px 6px rgba(0, 0, 0, .2);
    border-color: #212891
}

.demo-spin-icon-load {
    animation: ani-demo-spin 1s linear infinite;
}

.demo-spin-col {
    height: 400px;
    position: relative;

}

.ivu-form-item {
    margin-bottom: 0px
}

.middle{

    margin-right: 5px
}
</style>
