<template>
  <div class="c_t_conter">
    <div v-for="h in d_hearts">
      <h1>{{h.name}}</h1>
      <p v-html="h.content"></p>
    </div>
  </div>

</template>

<script>
export default {
  name: 'Trend',
  data() {
    return {
      d_hearts:[
		{name:"0",content:"heat 0"}
	  ]
    }
  },
  mounted() {
    this.f_heart()
  },
  methods: {
    f_heart(){
      this.f_query("/py/get_heart"+(this.d_hearts.length>0?"?last_heart_name="+this.d_hearts[0].name:""), (code, res) => {
        try{
          if(code){
             console.info("heart len",res.length)
            if(this.d_hearts.length==0||res.length>0&&res[res.length-1].name!=this.d_hearts[0].name){
              res.map(h=>this.d_hearts.splice(0,0,h))
            }
          }else{
            console.error("get heart is fail...")
          }
            setTimeout(this.f_heart,2000)
        }catch(e){
          console.error(e)
        }
      })
    },
    f_query(url, callback, params = {}, qtype = "get") {
      qtype = qtype.toLowerCase()
      if (qtype == "get") {
        params = {params: params}
      }
      const axios = require("axios")
      axios[qtype](url, params).then(resp => {
        try {
          callback(resp.status == 200, resp.data)
        } catch (e) {
          console.error(e)
          callback(0)
        }
      }).catch(e => console.error(e))
    }
  }
}
</script>

<style>
.c_t_conter {
  width: 100%;
  height: 100%;
}

</style>
