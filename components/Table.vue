<template>
  <div class="c_conter">
    <div class="c_tools">
      <select class="c_months" @change="f_refush_rows" v-model="this_month">
        <option v-for="m in months" :value="m">{{ m }}</option>
      </select>
      <input type="search" placeholder="search" @search="f_search" class="c_search_button" v-model="search_str"/>
      <input type="button" value="+" @click="f_add" class="c_add_button">
      <input type="button" value="trend" @click="f_open_page('Trend')" class="c_trend_button">
      <input type="button" value="back" @click="f_back()" class="c_back_button">
    </div>
    <div class="c_table">
      <!--thead-->
      <div class="c_tr">
        <div v-for="th in theads" class="c_td">{{ th }}</div>
      </div>
      <!--tbody-->
      <div v-for="(tr,ri) in (search_rows!=-1?search_rows:rows)" class="c_tr">
        <div v-for="(td,di) in tr" class="c_td" @click="f_edit_cel(ri,di)">{{ td }}</div>
        <input @click="f_del_row(ri)" type="button" value="x" class="c_td"/>
      </div>
    </div>
  </div>

</template>

<script>
export default {
  name: 'Index',
  data() {
    return {
      months: [],
      this_month: "",
      search_str: "",
      search_rows: -1,
      theads: ["名称", "时间", "成本", "卖出价格"],
      rows: [["td1", "td2"], ["td3", "td4"]]
    }
  },
  mounted() {
    this.f_refush_months(this.f_refush_rows)
  },
  methods: {
    f_open_page(component) {
      console.info("open component...", component)
      this.$router.push({
        name: component,
        params: {month:this.this_month}
      })
    },
    f_back() {
      this.$router.back()
    },
    f_edit_cel(rindex, dindex) {
      if (dindex > 1) {
        if (this.search_rows != -1) {
          rindex = this.search_rows[rindex][this.search_rows[rindex].length - 1]
        }
        const inputStr = prompt("修改", this.rows[rindex][dindex])
        if (inputStr != null && confirm("确定修改'" + this.rows[rindex][dindex] + "'>'" + inputStr + "'?")) {
          this.rows[rindex][dindex] = inputStr.trim()
          this.f_save()
        }
      }
    },
    f_refush_months(callback) {
      this.f_query("/py/get_month_arr", (code, res) => {
        if (code) {
          this.months = res
          if (this.months.indexOf(this.this_month) < 0) {
            this.this_month = this.months[this.months.length-1]
          }
          if (typeof (callback) == "function") {
            callback()
          }
        }
      })
    },
    f_refush_rows(e,callback) {
      this.f_query("/py/get_month_data", (code, res) => {
        if (code) {
          this.rows = res.trim().split("\n").map(line => line.split(",")).sort((a, b) => {
            return b[1].replace(/\//g, "") - a[1].replace(/\//g, "")
          })
          this.rows.splice(0, 1)
          this.f_search(null,callback)
        }
      }, {month: this.this_month})
    },
    f_search(e,callback) {
      try {
        if (this.search_str == "") {
          this.search_rows = -1
        } else {
          this.search_rows = JSON.parse(JSON.stringify(this.rows)).map((r, i) => {
            r.push("" + i);
            return r
          })
            .filter(r => r[0].startsWith(this.search_str) || r[0].endsWith(this.search_str) || r[0].indexOf(this.search_str) >= 0)
        }
        if(typeof callback=="function"){
          callback()
        }
      } catch (e1) {
        console.error(e1)
      }
    },
    f_add(e) {
      try {
        const inputStr = prompt("add 'name,300,0'")
        if (inputStr != null) {
          const input_arr = inputStr.trim().replace(/，/g, ",").split(",")
          if (input_arr.length > 1 && input_arr[0].trim() != "" && input_arr[1] > 0) {
            //init data
            input_arr[1] = parseFloat(input_arr[1])
            if (input_arr.length < 3) {
              input_arr.push(0)
            }
            const day = new Date().toJSON().split("T")[0].replace(/-/g, "/")
            input_arr.splice(1, 0, day)
            //push
            if (confirm("确认保存'" + input_arr.join(",") + "'?")) {
              const month = day.substr(0, day.lastIndexOf("/")).replace("/", "")
              if (this.months.indexOf(this.this_month) < 0) {
                this.rows = [input_arr]
                this.f_save()
              }else{
                //切换到要添加数据的月份
                this.this_month = month
                this.f_refush_rows(null,()=>{
                  this.rows.push(input_arr)
                  this.f_save()
                })
              }
            }
          } else {
            alert("输入有误!")
          }
        }
      } catch (e) {
        alert(e.stack)
      }
    },
    f_save() {
      this.f_query("/py/add_table_data?month=" + this.this_month, (code, res) => {
        alert("保存结果" + code)
        this.f_refush_months()
        this.f_refush_rows()
      }, [this.theads].concat(this.rows).map(r => r.join(",")).join("\n"), "post")
    },
    f_query(url, callback, params = {}, qtype = "get") {
      qtype = qtype.toLowerCase()
      if (qtype == "get") {
        params = {params: params}
      } else {
        params = typeof (params) == "string" ? params : JSON.stringify(params)
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
    },
    f_del_row(ri) {
      if (this.search_rows != -1) {
        ri = this.search_rows[ri][this.search_rows[ri].length - 1]
      }
      if (confirm("确定删除'" + this.rows[ri].join("','") + "'?")) {
        this.rows.splice(ri, 1)
        this.f_save()
      }
    }
  }
}
</script>

<style>
.c_conter {
  width: 100%;
  height: 100%;
}

.c_tools {
    width: fit-content;
    display: inline-flex;
    margin-bottom:10px;
}

.c_months,.c_search_button, .c_add_button, .c_trend_button,.c_back_button{
  height: 40px;
  border-radius: 5px;
  margin-left:5px;
}

.c_add_button {
  width: 40px;
}


.c_table {
  width: 100%;
  height: 80%;
  display: table;
}

.c_tr {
  display: table-row;
}

.c_td {
  display: table-cell;
  font-size: 15px;
  line-height: 15px;
  padding: 0 5px;
  white-space: nowrap;
}
</style>
