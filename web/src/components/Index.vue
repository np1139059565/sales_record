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
      <div v-for="p in d_phones" class="c_phone" :style="p.style" @click="f_click_phone(p)" :title="JSON.stringify(p)">
        {{p.wifi_device}}
      </div>
      <div class="c_phone c_padd" @click="f_add_phone()">+</div>
    </div>
    <div v-for="(h,i) in d_monitors">
      <p v-html="new Date(h.time*1000).toJSON().split('T')[1]" :style="{'color':i==0?'red':''}"></p>
      <p v-html="h.content" :style="{'color':i==0?'red':''}"></p>
    </div>
    <div class="c_loading" ref="loading1"></div>
  </div>
</template>

<script>
export default {
  name: 'Trend',
  data() {
    return {
      d_heart_id:-1,
      d_heart_time:1647949908.3097613,
      d_last_connect_time:1647949908.3097613,
      d_phones:[
        // {"wifi_device": "192.168.1.7:5555","local_device":"259e9dee","search_button":"900 2200","search_str":"oppo find x,2", "heart_time": 1648294339.938166}
      ],
      d_monitors:[
        //{time:"24643345.4666",content:"heat 0"}
      ],
    }
  },
  mounted() {
    this.f_init_base64()
    //stop heart
    if(this.d_heart_id>=0){
      clearInterval(this.d_heart_id)
      this.d_heart_id=-1
      console.info("stop heart")
    }
    //start new heart
    this.d_heart_id=setInterval(()=>{
      //time heart
      this.f_query("/py/get_time",(code,str)=>this.d_heart_time=str)
      //monitor heart
      this.f_monitor_heart()
      //phone heart
      if(this.$refs.parr1.classList.contains("c_parr_close")){
        this.f_phone_heart()
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
    f_add_phone(e,inputStr=",1;1000 2200;192.168.1.1:5555"){
      //get local device
      this.f_query_only("/py/get_adb_devices",(code,msg)=>{
        const local_device=msg.split("\r\n")[1].split("\t")[0]
        inputStr = prompt("新增手机(连接wifi>打开开发者模式>打开USB调试>插入电脑(只能插一台手机))>修改搜索坐标>修改ip和端口(不能重复)", inputStr+";"+local_device)
        if(inputStr!=null){
          const inputArr=inputStr.trim().split(";")
          if(this.d_phones.filter(p=>p.wifi_device==inputArr[2].trim()
          ||p.wifi_device.split(":")[1]==inputArr[2].trim().split(":")[1]).length>0){
            alert("ip或端口重复!")
            //clean local_device
            this.f_add_phone(e,inputStr.replace(";"+inputArr[3].trim(),""))
          }else{
            this.f_query_only("/py/add_phone?wifi_device="+inputArr[2].trim()+"&local_device="+inputArr[3].trim()
            +"&search_str="+inputArr[0].trim()+"&search_button="+inputArr[1].trim(),(code,msg)=>{
              if(code){
                alert("添加成功!")
              }else{
                alert(msg)
                this.f_add_phone(e,inputStr)
              }
            })
          }
        }
      })
    },
    f_click_phone(pinfo,params,inputStr){
      //init input str
      var isone=false
      if(inputStr==null){
        isone=true
        inputStr=prompt("打开新扫描(使用~连接数字(1代表全部,写了1就不能再写其他的数字了);搜索多种机型时,使用\\n换行)", pinfo.search_str)
      }
      //open scan..
      if(inputStr!=null){
        //init params
        if(params==null){
          params="?wifi_device="+pinfo.wifi_device+
          "&search_button="+pinfo.search_button+"&search_str="+inputStr
        }
        //start
        this.f_query_only("py/phone_start"+params,(code,msg)=>{
          if(code){
          }else if(isone&&confirm("启动失败,尝试连接数据线再试试!")){
            //re start only
            this.f_click_phone(pinfo,params+"&local_device="+pinfo.local_device,inputStr)
          }
        },true)
      }else if(confirm("确定要删除手机吗?")){
        //delete
        this.f_query("py/phone_delete?wifi_device="+pinfo.wifi_device,(code)=>alert("删除结果:"+code))
      }
    },
    f_open_parr(){
      this.$refs.parr1.className="c_parr"
    },
    f_close_parr(){
      this.$refs.parr1.className="c_parr c_parr_close"
    },
    f_phone_heart(){
      this.f_query("/py/get_phones", (code, phones) => {
        try{
          if(code){
            //  console.info("phone len",phonearr.length)
            this.d_phones=phones.map(p=>{
              //颜色标记
              p.style=("background:"+(this.d_heart_time-p.heart_time>15?"yellow":"green"))
              return p
            })
          }
        }catch(e){
          console.error(e)
        }
      })
    },
    f_init_base64(){
      window.Base64= {
        _keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
        encode: function (e) {
          var t = "";
          var n, r, i, s, o, u, a;
          var f = 0;
          e = Base64._utf8_encode(e);
          while (f < e.length) {
            n = e.charCodeAt(f++);
            r = e.charCodeAt(f++);
            i = e.charCodeAt(f++);
            s = n >> 2;
            o = (n & 3) << 4 | r >> 4;
            u = (r & 15) << 2 | i >> 6;
            a = i & 63;
            if (isNaN(r)) {
              u = a = 64
            } else if (isNaN(i)) {
              a = 64
            }
            t = t + this._keyStr.charAt(s) + this._keyStr.charAt(o) + this._keyStr.charAt(u) + this._keyStr.charAt(a)
          }
          return t
        },
        decode: function (e) {
          var t = "";
          var n, r, i;
          var s, o, u, a;
          var f = 0;
          e = e.replace(/[^A-Za-z0-9+/=]/g, "");
          while (f < e.length) {
            s = this._keyStr.indexOf(e.charAt(f++));
            o = this._keyStr.indexOf(e.charAt(f++));
            u = this._keyStr.indexOf(e.charAt(f++));
            a = this._keyStr.indexOf(e.charAt(f++));
            n = s << 2 | o >> 4;
            r = (o & 15) << 4 | u >> 2;
            i = (u & 3) << 6 | a;
            t = t + String.fromCharCode(n);
            if (u != 64) {
              t = t + String.fromCharCode(r)
            }
            if (a != 64) {
              t = t + String.fromCharCode(i)
            }
          }
          t = Base64._utf8_decode(t);
          return t
        }, _utf8_encode: function (e) {
          e = e.replace(/rn/g, "n");
          var t = "";
          for (var n = 0; n < e.length; n++) {
            var r = e.charCodeAt(n);
            if (r < 128) {
              t += String.fromCharCode(r)
            } else if (r > 127 && r < 2048) {
              t += String.fromCharCode(r >> 6 | 192);
              t += String.fromCharCode(r & 63 | 128)
            } else {
              t += String.fromCharCode(r >> 12 | 224);
              t += String.fromCharCode(r >> 6 & 63 | 128);
              t += String.fromCharCode(r & 63 | 128)
            }
          }
          return t
        }, _utf8_decode: function (e) {
          var t = "";
          var n = 0;
          var r =0;
          var c1 =0;
          var c2 = 0;
          while (n < e.length) {
            r = e.charCodeAt(n);
            if (r < 128) {
              t += String.fromCharCode(r);
              n++
            } else if (r > 191 && r < 224) {
              c2 = e.charCodeAt(n + 1);
              t += String.fromCharCode((r & 31) << 6 | c2 & 63);
              n += 2
            } else {
              c2 = e.charCodeAt(n + 1);
              var c3 = e.charCodeAt(n + 2);
              t += String.fromCharCode((r & 15) << 12 | (c2 & 63) << 6 | c3 & 63);
              n += 3
            }
          }
          return t
        }
      }
    },
    f_monitor_heart(){
      this.f_query("/py/get_monitor_last_times"+(this.d_monitors.length>0?"?last_heart_time="+this.d_monitors[0].time:""), (code, times) => {
        try{
          if(code){
            //  console.info("monitor len",times.length)
            if(this.d_monitors.length==0||times.length>0&&times[times.length-1]!=this.d_monitors[0].time){
              this.f_play_tts()
              times.map(time=>this.f_query("/py/get_monitor_info?time="+time,(code,content)=>{
                this.d_monitors.splice(0,0,{
                  time:time,
                  content:Base64.decode(content).replace(/\$/g,"<br>")
                })
              }))
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
    f_query_only(url,callback,params={}){
      this.f_query(url,callback,params,"get",true)
    },
    f_query(url, callback, params = {}, qtype = "get",showLoading=false) {
      if(showLoading){
        this.$refs.loading1.style.display="block"
      }
      qtype = qtype.toLowerCase()
      if (qtype == "get") {
        params = {params: params}
      }
      const axios = require("axios")
      axios[qtype](url, params).then(resp => {
        if(showLoading){
          this.$refs.loading1.style.display=""
        }
        callback(resp.status == 200, resp.data)
      })
      .catch(e => {
        if(showLoading){
          this.$refs.loading1.style.display=""
        }
        if(e.response.status==500){
          callback(false,e.response.data)
        }else console.error(e)
      })
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
.c_loading{
  width:100%;
  height:100%;
  position: absolute;
  top:0;
  left:0;
  cursor: progress;
  background: rgba(255,255,255,0.5);
  display: none;
}
</style>
