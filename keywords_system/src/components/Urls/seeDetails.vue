<template>
<div class="Urls-seeDetail">
    <i-modal v-model="DetailWindowShow" :title="'该项目一共有' + totalPage + '个分页。第' +currentPage +'页有' + dataLength +'个Url, 当前第' + (currentIndex + 1) + '个url: '  + website2 + '  状态: ' + currentUrlStatus" width="95" :closable="true" fullscreen :mask-closable="false" :scrollable="true" :styles="{top: '5px'}">
        <div class="Urls-seeDetail-main" id="iframe-parent">
            <iframe v-if="DetailWindowShow" :key="refreshKey" id='iframe' ref="iframe" class="Urls-seeDetail-iframe" :src="website2" frameborder="3" bordercolor=red></iframe>
            <div class="Urls-seeDetail-operate">
                <i-button class="Urls-seeDetail-operate-button" type="warning" size="large" :disabled="currentUrlStatus === '无效'" @click="setInvalid" icon="md-warning">设为无效</i-button>
                <i-button class="Urls-seeDetail-operate-button" type="success" size="large" :disabled="currentUrlStatus !== '无效'" @click="setValid" icon="md-medkit">设为有效</i-button>
                <i-button class="Urls-seeDetail-operate-button speccial2" type="primary" size="large" @click="refresh" icon="md-refresh">刷新当前</i-button>
                <i-button class="Urls-seeDetail-operate-button speccial" type="info" size="default" @click="moveLast" :disabled="currentPage=== 1">上一页</i-button>
                <i-button class="Urls-seeDetail-operate-button" type="info" size="large" shape="circle" @click="moveUp" :disabled="currentIndex === 0 && currentPage === 1">上一个</i-button>
                <i-button class="Urls-seeDetail-operate-button" type="info" size="large" shape="circle" @click="moveDown" :disabled="currentIndex === (dataLength -1) &&  currentPage === totalPage">下一个</i-button>
                <i-button class="Urls-seeDetail-operate-button" type="info" size="default" @click="moveNext" :disabled="currentPage === totalPage">下一页</i-button>
            </div>
        </div>
        <div slot="footer">
            <i-button type="default" size="large" @click="modalCancel('')">关闭</i-button>
        </div>
    </i-modal>
</div>
</template>

<script>
export default {
    name: 'seeDetail',
    data() {
        return {
            //disabledNow: false,
            refreshKey: 1,
            DetailWindowShow: JSON.parse(JSON.stringify(this.DetailWindowShow2)),
            currentIndex: JSON.parse(JSON.stringify(this.detailIndex)),
            // website2: JSON.parse(JSON.stringify(this.website)),
            currentPage: JSON.parse(JSON.stringify(this.currentPageNum)),
            totalPage: JSON.parse(JSON.stringify(this.totalPageNum)),
        }
    },
    mounted() {},
    props: ['website', 'detailIndex', 'pageData', 'currentPageNum', 'totalPageNum', 'DetailWindowShow2'],
    computed: {
        website2: function () {
            //console.log('this.pageData.length', this.pageData.length)
            if (this.pageData.length === 0) {
                // console.log('未开始')
                return 'https://www.stockhey.com'
            } else {
                // console.log('this.pageData[this.currentIndex]',this.pageData,this.currentPage, this.currentIndex)
                // console.log(this.pageData, this.currentIndex)
                return this.pageData[this.currentIndex]['rootUrl']
            }
        },
        currentUrlStatus: function () {
            //console.log('this.pageData.length', this.pageData.length)
            if (this.pageData.length === 0) {
                // console.log('未开始')
                return '未开始'
            } else {
                return this.pageData[this.currentIndex]['status']
            }
        },
        dataLength: function () {
            //console.log('this.pageData.length', this.pageData.length)
            return this.pageData.length
        }
    },
    beforeDestroy() {},
    methods: {
        //...mapMutations(['changeDetailWindowShow']),
        refresh: function () {
            this.refreshKey = this.refreshKey + 1
        },
        setInvalid: function () {
            // 注意，此处有一个bug ，或者说也不是。就是当快速的连续单击 按钮时，会导致功能失常报错。因为 每一次点击都 需要跟父组件通信，父组件 将修改的数据传给
            // 本（子）组件，这个是需要时间的，不是瞬时完成的。当数据还没到达，又点击按钮发起新的请求，会导致数据 丢失。这种情况下，请重新进入该功能！！！

            // 找到当前 页面的 uid
            let self = this
            let uid = self.pageData[self.currentIndex]['_id']['$oid']
            //console.log(uid)
            // 应该把index也发出去，重置外面的 index
            self.$emit('tagInvalid', {
                'uid': uid,
                'index': self.currentIndex
            })
        },
        setValid: function () {
            // 注意，此处有一个bug ，或者说也不是。就是当快速的连续单击 按钮时，会导致功能失常报错。因为 每一次点击都 需要跟父组件通信，父组件 将修改的数据传给
            // 本（子）组件，这个是需要时间的，不是瞬时完成的。当数据还没到达，又点击按钮发起新的请求，会导致数据 丢失。这种情况下，请重新进入该功能！！！

            // 找到当前 页面的 uid
            let self = this
            let uid = self.pageData[self.currentIndex]['_id']['$oid']
            //console.log(uid)
            // 应该把index也发出去，重置外面的 index
            self.$emit('tagValid', {
                'uid': uid,
                'index': self.currentIndex
            })
        },
        modalOk() {

        },
        modalCancel() {
            //this.changeDetailWindowShow(false)
            //this.$emit('update:DetailWindowShow2', false)
            this.DetailWindowShow = false
        },
        moveLast: function () {
            //上一页
            if (this.currentPage > 1) {
                // 那么发出事件，要求 父组件 获取上一页数据， 并且 从上一页最后一个开始显示，并将数据 重新传入
                // this.disabledNow = true
                this.$emit('askForPrePage')
            }
        },
        moveNext: function () {
            //下一页
            if (this.currentPage < this.totalPage) {
                // 那么发出事件，要求 父组件 获取下一页数据， 并且 从下一页第一个开始显示，并将数据 重新传入
                // this.disabledNow = true
                this.$emit('askForNextPage')
            }
        },
        moveUp: function () {
            // 上一项
            // 注意，此处有一个bug ，或者说也不是。就是当快速的连续单击 按钮时，会导致功能失常报错。因为 每一次点击都 需要跟父组件通信，父组件 将修改的数据传给
            // 本（子）组件，这个是需要时间的，不是瞬时完成的。当数据还没到达，又点击按钮发起新的请求，会导致数据 丢失。这种情况下，请重新进入该功能！！！
            let self = this
            self.currentIndex = self.currentIndex - 1
            //console.log(self.currentIndex)
            if (self.currentIndex === -1) {
                if (self.currentPage > 1) {
                    // 那么发出事件，要求 父组件 获取上一页数据， 并且 从上一页最后一个开始显示，并将数据 重新传入
                    // this.disabledNow = true
                    self.$emit('askForPrePage')
                }
            }
            // self.website2 = self.pageData[self.currentIndex]['rootUrl']
            // console.log(self.currentIndex,self.website2)
        },
        moveDown: function () {
            // 下一项
            // 注意，此处有一个bug ，或者说也不是。就是当快速的连续单击 按钮时，会导致功能失常报错。因为 每一次点击都 需要跟父组件通信，父组件 将修改的数据传给
            // 本（子）组件，这个是需要时间的，不是瞬时完成的。当数据还没到达，又点击按钮发起新的请求，会导致数据 丢失。这种情况下，请重新进入该功能！！！
            let self = this
            self.currentIndex = self.currentIndex + 1
            //console.log(self.currentIndex)
            if (self.currentIndex === self.dataLength) {
                if (self.currentPage < self.totalPage) {
                    // 那么发出事件，要求 父组件 获取下一页数据， 并且 从下一页第一个开始显示，并将数据 重新传入
                    // self.disabledNow = true
                    self.$emit('askForNextPage')
                }
            }
            // self.website2 = self.pageData[self.currentIndex]['rootUrl']
            // console.log(self.currentIndex,self.website2)
        }
    }
}
</script>

<style scoped>
.Urls-seeDetail-iframe {
    height: 600px;
    width: 90%
}

.Urls-seeDetail-main {
    display: flex
}

.Urls-seeDetail-operate {
    display: flex;
    flex-direction: column;
}

.Urls-seeDetail-operate-button {
    margin: 20px
}

.Urls-seeDetail-operate .speccial {
    margin-top: 50px
}

.Urls-seeDetail-operate .speccial2 {
    margin-top: 50px
}
</style>
