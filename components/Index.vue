<template>
  <div class="c_t_conter">
    <audio ref="audio1" controls="controls" class="c_audio">
      <source src="/static/audio/11981.mp3" type="audio/mpeg" />
    </audio>
    <div class="c_tools">
      <input type="button" value="table" @click="f_open_page('Table')" class="c_table_button">
    </div>
    <br>
    <h1 class="c_head">{{ new Date(d_heart_time * 1000).toJSON() }}</h1>
    <div class="c_parr c_parr_close" ref="parr1" @mouseover="f_open_parr()" @mouseout="f_close_parr()">
      <div v-for="p in d_phones" :key="p" class="c_phone" :style="p.style" @click="f_click_phone(p)"
        :title="JSON.stringify(p)">
        {{ p.wifi_device }}
      </div>
      <div class="c_phone c_padd" @click="f_save_phone()">+</div>
    </div>
    <div v-for="(h, i) in d_monitors" :key="i">
      <p v-html="new Date(h.time * 1000).toJSON().split('T')[1]" :style="{ 'color': i == 0 ? 'red' : '' }"></p>
      <p v-html="h.content" :style="{ 'color': i == 0 ? 'red' : '' }"></p>
    </div>
    <div class="c_loading" ref="loading1"></div>
    <!-- 弹框 -->
    <div class="c_modal-container" ref="dialog">
      <!-- 关闭按钮 -->
      <button class="c_close-btn" @click="dialog_closeModal">关闭</button>
      <!-- 下拉框 -->
      <select class="c_device" v-model="d_selected_device" @change="f_change_device()">
        <option v-for="option in d_devices" :key="option.value" :value="option.value">{{ option.label }}</option>
      </select>
      <!-- 表格 -->
      <table class="c_table">
        <thead>
          <tr>
            <th>text</th>
            <th>type</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <draggable v-model="d_xml_selecteds" :options="dragOptions" style="display: contents;">
            <tr v-for="(item, i) in d_xml_selecteds" :key="i">
              <td>
                <template v-if="d_xml_search.length > 0">
                  <span>search:{{ d_xml_search }}</span>
                </template>
                <div class="c_...">
                  <select class="c_xml_node" v-model="d_xml_selecteds[i]" :title="JSON.stringify(d_xml_selecteds[i])"
                    @keyup="f_xml_search_switch" @change="f_xml_change" :i="i">
                    <option v-for="x in item.defxmls" :value="x" :style="x.style">{{ JSON.stringify(x) }}</option>
                  </select>
                </div>
              </td>
              <td>
                <select class="c_handtype" v-model="item['hand_type']" :i="i"
                  :bounds="d_xml_selecteds[i]['hand_type'].bounds" @change="f_hand_type_change">
                  <option v-for="option in item.def_hand_types" :value="option">{{ option.label }}</option>
                </select>
                <template v-if="item['hand_type'].bounds != null">
                  <input v-model="item['hand_type'].bounds" style="width:120px"
                    title="bounds:按照[x,y][x,y]格式输入,若为空则根据左边选中的节点来动态计算,所以必须存在一个">
                </template>
                <template v-if="item['hand_type'].value != null">
                  <input title="value:字符串" v-model="item['hand_type'].value" style="width:50px">
                </template>
                <template v-if="item['hand_type'].speed != null">
                  <select v-model="item['hand_type'].speed" title="speed:滑动速度,速度越快划的越长">
                    <option v-for="s in [0.1, 0.2, 0.4, 0.8]" :value="s">{{ s }}</option>
                  </select>
                </template>
              </td>
              <td>
                <!-- 拖拽手柄和删除按钮放在一起 -->
                <span class="c_draggable-buttons">
                  <span class="c_drag-handle">☰</span>
                  <span class="c_drag-test" @click="f_dialog_test(i)">测试</span>
                  <button class="c_delete-btn" @click="dialog_deleteItem(i)">删除</button>
                </span>
              </td>
            </tr>
          </draggable>
        </tbody>
      </table>
      <!-- 添加按钮 -->
      <button class="c_add-btn" @click="dialog_addItem">添加</button>
      <button class="c_submit-btn" @click="dialog_submit">提交</button>
    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable';
export default {
  name: 'Trend',
  components: {
    draggable
  },
  data() {
    return {
      d_heart_id: -1,
      d_heart_time: 1647949908.3097613,
      d_last_connect_time: 1647949908.3097613,
      d_phones: [
        // {"wifi_device": "192.168.1.7:5555","local_device":"259e9dee","search_button":"900 2200","search_str":"oppo find x,2", "heart_time": 1648294339.938166}
      ],
      d_monitors: [
        //{time:"24643345.4666",content:"heat 0"}
      ],
      d_devices: [],
      d_selected_device: '',
      d_defxmls: [],
      d_xml_selecteds: [
        // { text: '', 'resource-id': 'com.aihuishou.opt:id/cl_info', class: 'android.view.ViewGroup', bounds: '[32,400][1048,653]', 'hand_type': { label: 'click', type: 'click', value: '' } },
        // { text: '', 'resource-id': 'com.aihuishou.opt:id/cl_info', class: 'android.view.ViewGroup', bounds: '[32,400][1048,653]', 'hand_type': { label: 'click', type: 'click', value: '' } },
        // { text: '', 'resource-id': 'com.aihuishou.opt:id/cl_info', class: 'android.view.ViewGroup', bounds: '[32,400][1048,653]', 'hand_type': { label: 'click', type: 'click', value: '' } },
      ],
      d_def_hand_nodes: [
        { label: '点击', type: 'click', bounds: '' },
        { label: '滑动', type: 'slice', bounds: '', speed: '' },
        { label: '输入', type: 'input', value: '' },
        { label: '刷新', type: 'dump' }
      ],
      dragOptions: {
        handle: '.c_drag-handle' // 拖拽手柄的 CSS 类名
      },
      d_xml_search: ''
    }
  },
  mounted() {
    this.f_init_base64()
    //stop heart
    if (this.d_heart_id >= 0) {
      clearInterval(this.d_heart_id)
      this.d_heart_id = -1
      console.info("stop heart")
    }
    //start new heart
    // this.d_heart_id = setInterval(() => {
    //   //time heart
    //   this.f_query("/py/get_time", (code, str) => this.d_heart_time = str)
    //   //monitor heart
    //   this.f_monitor_heart()
    //   //phone heart
    //   if (this.$refs.parr1.classList.contains("c_parr_close")) {
    //     this.f_phone_heart()
    //   }
    // }, 2000)
  },
  methods: {
    f_dialog_test(i) {
      const tdata = this.d_xml_selecteds[i];
      console.info('test', this.d_xml_selecteds[i]);
      this.f_query_only('/py/get_ui_by_uiautomator2/' + tdata['hand_type'].type + '?device=' + this.d_selected_device
        + '&node_info='+JSON.stringify(tdata),
        (code, msg) => {
          alert(code + ':' + msg)
        })
    },
    f_hand_type_change(e) {
      if (this.d_xml_selecteds[e.target.getAttribute('i')]['hand_type'].bounds != null) {
        this.d_xml_selecteds[e.target.getAttribute('i')]['hand_type'].bounds = e.target.getAttribute('bounds');
      }
    },
    f_open_page(component) {
      console.info("open component...", component)
      //stop heart
      if (this.d_heart_id >= 0) {
        clearInterval(this.d_heart_id)
        this.d_heart_id = -1
        console.info("stop heart")
      }
      //to page...
      this.$router.push({
        name: component,
        params: { month: this.this_month }
      })
    },
    f_play_tts() {
      //百度
      try {
        //var url = "https://fanyi.baidu.com/gettts?lan=zh&text="+encodeURI(str)+"&spd=5&source=web"
        //this.d_audio = "/static/audio/11981.mp3"
        this.$refs.audio1.play()
      } catch (e) {
        console.error(e.stack)
      }
    },
    f_save_phone() {
      //get device list
      this.f_query_only("/py/adb/devices", (code, msg) => {
        if (code) {
          this.$refs.dialog.style.display = 'block';
          this.d_devices = msg.split("\r\n").filter((v, i) => i > 0)
            .map(line => line.split("\t")[0]).map(d => { return { value: d, label: d } })
          if (this.d_devices.length > 0) {
            this.d_selected_device = this.d_devices[0].value
            this.f_change_device()
          }
        } else {
          alert(msg);
        }
      })
    },
    f_click_phone(pinfo, params, inputStr) {
      //init input str
      var isone = false
      if (inputStr == null) {
        isone = true
        inputStr = prompt("打开新扫描(使用~连接数字(1代表全部,写了1就不能再写其他的数字了);搜索多种机型时,使用\\n换行)", pinfo.search_str)
      }
      //open scan..
      if (inputStr != null) {
        //init params
        if (params == null) {
          params = "?wifi_device=" + pinfo.wifi_device +
            "&search_button=" + pinfo.search_button + "&search_str=" + inputStr
        }
        //start
        this.f_query_only("py/phone_start" + params, (code) => {
          if (code) {

          } else if (isone && confirm("启动失败,尝试连接数据线再试试!")) {
            //re start only
            this.f_click_phone(pinfo, params + "&local_device=" + pinfo.local_device, inputStr)
          }
        }, true)
      } else if (confirm("确定要删除手机吗?")) {
        //delete
        this.f_query("py/phone_delete?wifi_device=" + pinfo.wifi_device, (code) => alert("删除结果:" + code))
      }
    },
    f_open_parr() {
      this.$refs.parr1.className = "c_parr"
    },
    f_close_parr() {
      this.$refs.parr1.className = "c_parr c_parr_close"
    },
    f_phone_heart() {
      this.f_query("/py/get_phones", (code, phones) => {
        try {
          if (code) {
            //  console.info("phone len",phonearr.length)
            this.d_phones = phones.map(p => {
              //颜色标记
              p.style = ("background:" + (this.d_heart_time - p.heart_time > 15 ? "yellow" : "green"))
              return p
            })
          }
        } catch (e) {
          console.error(e)
        }
      })
    },
    f_init_base64() {
      window.Base64 = {
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
          var r = 0;
          var c1 = 0;
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
    f_monitor_heart() {
      this.f_query("/py/get_monitor_last_times" + (this.d_monitors.length > 0 ? "?last_heart_time=" + this.d_monitors[0].time : ""), (code, times) => {
        try {
          if (code) {
            //  console.info("monitor len",times.length)
            if (this.d_monitors.length == 0 || times.length > 0 && times[times.length - 1] != this.d_monitors[0].time) {
              this.f_play_tts()
              times.map(time => this.f_query("/py/get_monitor_info?time=" + time, (code, content) => {
                this.d_monitors.splice(0, 0, {
                  time: time,
                  content: Base64.decode(content).replace(/\$/g, "<br>")
                })
              }))
            }
          } else {
            console.error("get monitor is fail...")
            this.d_monitor_style = "color:red"
          }
        } catch (e) {
          console.error(e)
        }
      })
    },
    f_query_only(url, callback, params = {}) {
      this.f_query(url, callback, params, "get", true)
    },
    f_query(url, callback, params = {}, qtype = "get", showLoading = false) {
      if (showLoading) {
        this.$refs.loading1.style.display = "block"
      }
      qtype = qtype.toLowerCase()
      if (qtype == "get") {
        params = { params: params }
      }
      const axios = require("axios")
      axios[qtype](url, params).then(resp => {
        if (showLoading) {
          this.$refs.loading1.style.display = ""
        }
        callback(resp.status == 200, resp.data)
      })
        .catch(e => {
          if (showLoading) {
            this.$refs.loading1.style.display = ""
          }
          if (e.response.status == 500) {
            callback(false, e.response.data)
          } else console.error(e)
        })
    },
    dialog_closeModal(e) {
      this.$refs.dialog.style.display = 'none';
    },
    dialog_addItem() {
      if (this.d_defxmls.length > 0) {
        this.d_xml_selecteds.push(this.d_defxmls[0]);
      }
    },
    dialog_deleteItem(i) {
      this.d_xml_selecteds.splice(i, 1);
    },
    f_change_device() {
      this.f_query_only("/py/get_ui_by_uiautomator2/dump?device=" + this.d_selected_device, (code, msg) => {
        if (code) {
          this.d_xmls = [];
          var parser = new DOMParser();
          var xmlDoc = parser.parseFromString(msg, "text/xml");
          var nodes = this.f_get_all_last_node(xmlDoc);

          for (var i = 0; i < nodes.length; i++) {
            var text = nodes[i].getAttribute("text");
            if(text.trim().length==0){
              text = nodes[i].getAttribute("content-desc");
            }
            var resourceid = nodes[i].getAttribute("resource-id");
            var c = nodes[i].getAttribute("class");
            var bounds = nodes[i].getAttribute("bounds");
            const node = {
              text: text, 'resource-id': resourceid, class: c, bounds: bounds,
              'hand_type': this.d_def_hand_nodes[0]
            }
            // node['hand_type'].bounds = bounds
            this.d_defxmls.push(node);
          }
          if (this.d_defxmls.length > 0) {
            this.d_xml_selecteds = [this.d_defxmls[0]];
          }
        } else {
          alert(msg)
        }
      });
    },
    f_get_all_last_node(e, nodearr) {
      if (e.children.length == 0) {
        if (nodearr == null) {
          nodearr = [];
        } else {
          nodearr.push(e);
        }
      } else {
        for (var i = 0; i < e.children.length; i++) {
          nodearr = this.f_get_all_last_node(e.children[i], nodearr);
        }
      }
      return nodearr;
    },
    f_xml_search_switch(e) {
      console.info(e.key);
      if (e.key.length == 1) {
        this.d_xml_search += e.key;
      } else if (e.key == 'Backspace') {
        this.d_xml_search = this.d_xml_search.substring(0, this.d_xml_search.length - 1);
      }
      this.d_defxmls.map(line =>
        line.style = 'display:' + (JSON.stringify(line).indexOf(this.d_xml_search) >= 0 || this.d_xml_search == '' ? 'block' : 'none'));
    },
    f_xml_change(e){
      this.d_xml_selecteds[e.target.getAttribute('i')]['hand_type'].bounds=this.d_xml_selecteds[e.target.getAttribute('i')].bounds
    },
    dialog_submit() {
      console.info(this.d_xml_selecteds)
      this.f_query_only('/py/flask_server/f_save_phone?device=' + this.d_selected_device + "&hand_data=" + JSON.stringify(this.d_xml_selecteds),
        (code, msg) => {
          alert(msg)
        })
    }
  }
}
</script>

<style>
@import '../assets/css/Index.css';
</style>
