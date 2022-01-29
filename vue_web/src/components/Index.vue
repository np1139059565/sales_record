<template>
  
  <div id="i_conter">
    <input type="button" value="表格" @click="f_open_page('/table')">
    <input type="button" value="趋势图" @click="f_open_page('/trend')">
  </div>
</template>

<script>
export default {
  data () {
    return {
      msg: 'Welcome to Your Vue.js App'
    }
  },
  methods:{
      f_open_page(url,params={}){
        console.info("open page...",url)
        this.$router.push({
          path:url,
          query:{
            params:params
          }
        })
      }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 input{
   width:40%;
   height:30%;
 }
</style>
