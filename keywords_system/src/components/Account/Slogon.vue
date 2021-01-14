<template>
<div class="slogon">
    <div class="slogon-pic"></div>
    <div class="slogon-words">{{ slogon }}</div>
</div>
</template>

<script>
export default {
    name: 'Slogon',
    props: {
        slogon: String
    }
}
</script>

<style scoped>
.slogon {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    align-items: flex-start;
    margin: 100px auto;
}

.slogon-pic {
    height: 28px;
    width: 88px;
    background-image: url(../../assets/dbb2.png);
    background-repeat: no-repeat;
    background-position: 100%;
    background-size: 100% 100%;
}

@media (min-width: 500px) {
    .slogon-words {
        font-size: 4rem;
    }
}

.slogon-words {
    font-size: 3rem;
    color: #212891;
    font-weight: bold;
}
</style>
