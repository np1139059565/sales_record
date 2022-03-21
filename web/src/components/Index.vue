<template>
  <div class="c_t_conter">
    <audio ref="audio1" controls="controls" class="c_audio">
      <source src="/static/audio/11981.mp3" type="audio/mpeg" />
    </audio>
    <div class="c_tools">
      <input type="button" value="table" @click="f_open_page('Table')" class="c_table_button">
    </div>
    <br>
    <h1 class="c_head">{{new Date(d_heart_time*1000).toJSON()}}</h1>
    <div class="c_parr c_parr_close" ref="parr1" @mouseover="f_open_parr()" @mouseout="f_close_parr()">
      <div v-for="p in d_phones" class="c_phone" :style="p.style" @click="f_start_phone(p)">
        {{p.ip}}:{{p.port}}
      </div>
      <div class="c_phone c_padd" @click="f_add_phone()">+</div>
    </div>
    <div v-for="h in d_monitors">
      <p v-html="h.content"></p>
    </div>
  </div>

</template>

<script>
export default {
  name: 'Trend',
  data() {
    return {
      d_heart_id:-1,
      d_heart_time:"2022-03-20T11:43:02.112Z",
      d_phones:[
        // {ip:"192.168.1.157",port:5555,heart:0},
      ],
      d_monitors:[
        //{name:"0",content:"heat 0"}
      ],
    }
  },
  mounted() {
    //stop heart
    if(this.d_heart_id>=0){
      clearInterval(this.d_heart_id)
      this.d_heart_id=-1
      console.info("stop heart")
    }
    //start new heart
    this.d_heart_id=setInterval(()=>{
      this.f_query("/py/get_time",(code,str)=>this.d_heart_time=str)
      this.f_get_last_monitor()
      if(this.$refs.parr1.classList.contains("c_parr_close")>=0){
        this.f_get_phones()
      }
    },2000)
  },
  methods: {
    f_open_page(component) {
      console.info("open component...", component)
      //stop heart
      if(this.d_heart_id>=0){
        clearInterval(this.d_heart_id)
        this.d_heart_id=-1
        console.info("stop heart")
      }
      //to page...
      this.$router.push({
        name: component,
        params: {month:this.this_month}
      })
    },
    f_play_tts(){
        //百度
        try{
          //var url = "https://fanyi.baidu.com/gettts?lan=zh&text="+encodeURI(str)+"&spd=5&source=web"
          //this.d_audio = "/static/audio/11981.mp3"
          this.$refs.audio1.play()
        }catch(e){
          console.error(e.stack)
        }
    },
    f_add_phone(e,inputStr="192.168.1.1:5555"){
      inputStr = prompt("新增手机(注意,必须在同一网段内)", inputStr)
      if(inputStr!=null){
        const iport=inputStr.trim().split(":")
        if(this.d_phones.filter(p=>p.ip==iport[0].trim()||p.port==iport[1].trim()).length>0){
          alert("ip或端口重复!")
          this.f_add_phone(e,inputStr)
        }else{
          this.f_query("/py/add_phone?ip="+iport[0].trim()+"&port="+iport[1].trim(),(code,msg)=>{
            if(code){
              alert("添加成功!")
            }else{
              alert(msg)
              this.f_add_phone(e,inputStr)
            }
          })
        }
      }
    },
    f_start_phone(pinfo){
      this.f_query("py/start_phone_command?ip="+pinfo.ip+"&port="+pinfo.port,(code)=>{
        if(!code)alert("启动失败!")
      })
    },
    f_open_parr(){
      this.$refs.parr1.className="c_parr"
    },
    f_close_parr(){
      this.$refs.parr1.className="c_parr c_parr_close"
    },
    f_get_phones(){
      this.f_query("/py/get_phones", (code, phonearr) => {
        try{
          if(code){
            //  console.info("phone len",phonearr.length)
            this.d_phones=phonearr.map(p=>{
              console.info(this.d_heart_time-p.heart_time)
              p.style=("background:"+(this.d_heart_time-p.heart_time>60?"yellow":"green"))
              return p
            })
          }else{
            console.error("get phone is fail...")
          }
        }catch(e){
          console.error(e)
        }
      })
    },
    f_get_last_monitor(){
      this.f_query("/py/get_last_monitor"+(this.d_monitors.length>0?"?last_heart_time="+this.d_monitors[0].name:""), (code, res) => {
        try{
          if(code){
            //  console.info("monitor len",res.length)
            if(this.d_monitors.length==0||res.length>0&&res[res.length-1].name!=this.d_monitors[0].name){
              this.f_play_tts()
              res.map(h=>this.d_monitors.splice(0,0,h))
            }
          }else{
            console.error("get monitor is fail...")
            this.d_monitor_style="color:red"
          }
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
html,body,div,h1{
  padding:0;
  margin:0;
}

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
    min-width:30px;
    min-height:30px;
    border:1px solid #CCC;
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
}
.c_padd{
  width:20px;
}
.c_parr_close .c_padd{
  display: none;
}
.c_add_button {
  width: 40px;
}

</style>
