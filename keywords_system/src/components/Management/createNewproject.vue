<template>
<div class="management-newProject">
    <i-button class="management-newProject-button" type="success" icon="md-add" @click="addProject()" :disabled="createProjectBottonStatus">新建项目</i-button>
    <i-modal v-model="modal1" title="创建新项目" :closable="false" :mask-closable="false" :scrollable="true">

        <div class="management-newProject-name">

            <i-form ref="formCustom" :model="formCustom" :rules="ruleCustom" :label-width="80">
                <i-formItem label="项目名称" prop="newProjectName">
                    <i-input class="management-newProject-name-input" type="text" v-model="formCustom.newProjectName" placeholder="请输入项目名称"></i-input>
                </i-formItem>

                <i-formItem v-for="(item, xindex) in shownformCustomItems" :key="xindex" :label="'分类 ' + item.index" :prop="item.value">
                    <i-row>
                        <i-col span="18">
                            <i-input type="text" v-model="item.value" placeholder="请输入分类名"></i-input>
                        </i-col>
                        <i-col span="4" offset="1">
                            <i-button @click="handleRemove(xindex)">删除</i-button>
                        </i-col>
                    </i-row>
                </i-formItem>
                <i-formItem>
                    <i-row>
                        <i-col span="12">
                            <i-button type="dashed" long @click="handleAdd" icon="md-add">添加分类</i-button>
                        </i-col>
                    </i-row>
                </i-formItem>
            </i-form>

        </div>
        <div slot="footer">
            <i-button type="text" size="large" @click="modalCancel('formCustom')">取消</i-button>
            <i-button type="primary" size="large" @click="modalOk('formCustom')">提交</i-button>
        </div>
    </i-modal>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'createNewproject',
    data() {
        const validateProject = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('请填写项目名称'));
            } else if (value.indexOf(" ") != -1 || value.indexOf("'") != -1 || value.indexOf('"') != -1 || value.indexOf('/') != -1) {
                callback(new Error("项目名称不能包含空格,\",','/'"));
            } else if (value.length >= 250) {
                callback(new Error("长度不能超过250个字符!"));
            } else if (value.startsWith('.') || value.startsWith('\\') || value.startsWith('.\\') || value.startsWith('..')) {
                callback(new Error("不能以'.'或'\\'或 '.\\'或 '..'开头"));
            } else {
                callback();
            }
        };
        return {
            formCustom: {
                newProjectName: '',
                items: [{
                    value: '',
                    index: 1,
                    status: 1
                }]
            },
            ruleCustom: {
                newProjectName: [{
                    validator: validateProject,
                    trigger: 'blur'
                }]
            },
            index: 1,
            createProjectBottonStatus: false,
            modal1: false
        }
    },
    computed: {
        ...mapState(['currentUserName']),
        shownformCustomItems: function () {
            let shownformCustomItemsData = []
            for (let element in this.formCustom.items) {
                if (this.formCustom.items[element].status !== 0) {
                    shownformCustomItemsData.push(this.formCustom.items[element])
                }
            }
            return shownformCustomItemsData
        }
    },
    beforeDestroy() {},
    methods: {
        handleAdd() {
            this.index++;
            this.formCustom.items.push({
                value: '',
                index: this.index,
                status: 1
            });
        },
        handleRemove(index) {
            // console.log(index)
            this.shownformCustomItems[index].status = 0;
        },
        modalOk(name) {
            let self = this
            self.index = 1
            // check 项目 是否为空
            self.$refs[name].validate((valid) => {
                if (valid) {
                    // console.log('验证成功')
                    self.modal1 = false
                    self.createProjectBottonStatus = false
                    // 得到 项目添加的有效数据，并返回到父组件
                    let newProjectName = self.formCustom.newProjectName
                    let categories = []
                    for (let myindex in self.shownformCustomItems) {
                        if (self.shownformCustomItems[myindex].value) {
                            categories.push({
                                'categoryName': self.shownformCustomItems[myindex].value
                            })
                        }
                    }
                    let projectInfo = {
                        'projectName': newProjectName,
                        'creater': localStorage.getItem('kwmUser'),
                        'categories': categories
                    }
                    // console.log(projectInfo)
                    this.$emit('createNeWProject', projectInfo)
                    // self.$Message.success('提交成功!');
                    self.formCustom.items = [{
                            value: '',
                            index: 1,
                            status: 1
                        }],

                        self.formCustom.newProjectName = ''
                    self.$refs[name].resetFields()

                } else {
                    // console.log('验证失败')
                    self.$Message.error('提交失败');
                    self.modal1 = true
                }
            })
        },
        modalCancel(name) {
            let self = this
            self.index = 1
            self.formCustom.items = [{
                value: '',
                index: 1,
                status: 1
            }]
            self.modal1 = false
            self.createProjectBottonStatus = false
            self.$refs[name].resetFields()
        },
        addProject: function () {
            this.createProjectBottonStatus = true
            this.modal1 = true
        },
    }
}
</script>

<style scoped>
.management-newProject-button {
    margin: 10px auto
}

.management-newProject-name {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px
}

.management-newProject-name-input {
    width: 200px
}

.management-newProject-namw-label {
    width: 80px
}

.management-newProject-name-input {
    width: 300px
}

.management-newProject-categories {
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
