<template>
<div id="app">
    <i-backTop :height="200"></i-backTop>
    <router-view />
</div>
</template>

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
}

#nav {
    padding: 30px;
}

#nav a {
    font-weight: bold;
    color: #2c3e50;
}

#nav a.router-link-exact-active {
    color: #42b983;

}

.ivu-card-body {
    padding: 16px 0px !important
}

.ivu-modal-body {
    padding: 3px 5px !important;
    margin-left: 5px !important;
    margin-right: 5px !important
}

.ivu-modal-header {
    padding: 5px 16px !important
}

.ivu-modal-footer {
    padding: 5px 18px !important
}
.ivu-layout.ivu-layout-has-sider .layout-content.ivu-layout-content{
    padding-top: 25px !important
}


</style>
