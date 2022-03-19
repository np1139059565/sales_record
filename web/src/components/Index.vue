<template>
  <div class="c_t_conter">
    <audio ref="audio1" controls="controls" class="c_audio">
      <source src="/static/audio/11981.mp3" type="audio/mpeg" />
    </audio>
    <div class="c_tools">
      <input type="button" value="table" @click="f_open_page('Table')" class="c_table_button">
      <input type="button" value="+" @click="f_open_page('Table')" class="c_add_button">
    </div>
    <br>
    <div class="c_parr c_parr_close" ref="parr1" @mouseover="f_open_parr()" @mouseout="f_close_parr()">
      <div v-for="p in d_phone_arr" class="c_phone">
        {{p.ip}}:{{p.port}}
      </div>
    </div>
    <div v-for="h in d_hearts">
      <h1 :style="d_heart_style">{{h.name}}</h1>
      <p v-html="h.content"></p>
    </div>
  </div>

</template>

<script>
export default {
  name: 'Trend',
  data() {
    return {
      d_phone_arr:[
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0},
        {ip:"192.168.1.157",port:5555,stat:0}
      ],
      d_heart_style:"color:green",
      d_hearts:[
        //{name:"0",content:"heat 0"}
      ]
    }
  },
  mounted() {
    this.f_heart()
  },
  methods: {
    f_open_page(component) {
      console.info("open component...", component)
      this.$router.push({
        name: component,
        params: {month:this.this_month}
      })
    },
    f_tts(str){
        //百度
        try{
          //var url = "https://fanyi.baidu.com/gettts?lan=zh&text="+encodeURI(str)+"&spd=5&source=web"
          //this.d_audio = "/static/audio/11981.mp3"
          this.$refs.audio1.play()
        }catch(e){
          console.error(e.stack)
        }
    },
    f_open_parr(){
      this.$refs.parr1.className="c_parr"
      
    },
    f_close_parr(){
      this.$refs.parr1.className="c_parr c_parr_close"
    },
    f_heart(){
      this.f_query("/py/get_heart"+(this.d_hearts.length>0?"?last_heart_name="+this.d_hearts[0].name:""), (code, res) => {
        try{
          if(code){
             console.info("heart len",res.length)
            if(this.d_hearts.length==0||res.length>0&&res[res.length-1].name!=this.d_hearts[0].name){
              this.f_tts()
              res.map(h=>this.d_hearts.splice(0,0,h))
            }
          }else{
            console.error("get heart is fail...")
            this.d_heart_style="color:red"
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
.c_parr,.c_tools {
    width: fit-content;
    display: inline-flex;
    margin-bottom:10px;
}

.c_audio,.c_table_button,.c_add_button{
  height: 40px;
  border-radius: 5px;
  margin-left:5px;
}
.c_audio{
  width:100%;
  padding:0;
  margin:0;
}
.c_parr{
    max-width: 80%;
    cursor: pointer;
    display: inline-block;
}
.c_phone{
  height:20px;
  margin:5px;
  border-radius: 5px;
  overflow: hidden;
  float: left;
  border: 1px solid;
  border-color: #ccc;
}
.c_phone:hover{
  border-color: #555;
}
.c_parr_close .c_phone{
  width:20px;
  color: rgba(255,255,255,0);
  background: green;
}
.c_add_button {
  width: 40px;
}
</style>
