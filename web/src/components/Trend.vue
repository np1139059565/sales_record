<template>
  <div class="c_t_conter">
    <div id="i_trend"></div>
    <div class="c_t_tools">
      <select class="c_t_months" @change="f_refush_trend" v-model="this_month">
        <option v-for="m in months" :value="m">{{ m }}</option>
      </select>
      <input type="button" value="back" @click="f_back()" class="c_t_back">
    </div>
  </div>

</template>

<script>
export default {
  name: 'Trend',
  data() {
    return {
      months: [],
      this_month: "",
      myChart: null,
      countries: [
        'buy_total',//进货成本
        'sell_total',//售价
        'profits_total'//利润
      ]
    }
  },
  mounted() {
    console.info("trend month...",this.$route.params.month)
    this.this_month=this.$route.params.month
    this.f_init_trend()
    this.f_refush_months(this.f_refush_trend)
  },
  methods: {
    f_back() {
      this.$router.back()
    },
    f_refush_months(callback) {
      this.f_query("/py/get_months", (code, res) => {
        if (code) {
          this.months = res
          if (this.months.indexOf(this.this_month) < 0) {
            this.this_month = this.months[0]
          }
          if (typeof (callback) == "function") {
            callback()
          }
        }
      })
    },
    f_refush_trend() {
      this.f_query("/py/get_data", (code, res) => {
        if (code) {
          const datasetWithFilters = [];
          const seriesList = [];
          const echarts = require("echarts")
          echarts.util.each(this.countries, function (country) {
            var datasetId = 'dataset_' + country;
            datasetWithFilters.push({
              id: datasetId,
              fromDatasetId: 'dataset_raw',
              transform: {
                type: 'filter',
                config: {
                  and: [
                    {dimension: 'time', gte: "1950/01/01", parser: 'time'},
                    {dimension: 'Country', '=': country}
                  ]
                }
              }
            });
            seriesList.push({
              type: 'line',
              datasetId: datasetId,
              showSymbol: false,
              name: country,
              endLabel: {
                show: true,
                formatter: function (params) {
                  var name = ""
                  switch (params.value[1]) {
                    case 'buy_total':
                      name = "进货成本"
                      break;
                    case 'sell_total':
                      name = "销售额"
                      break;
                    case 'profits_total':
                      name = "利润"
                      break;
                  }
                  return name + ':' + params.value[2];
                }
              },
              labelLayout: {
                moveOverlap: 'shiftY'
              },
              emphasis: {
                focus: 'series'
              },
              encode: {
                x: 'time',
                y: 'val',
                label: ['Country', 'val'],
                itemName: 'time',
                tooltip: ['val']
              }
            });
          });
          var option = {
            dataset: [
              {
                id: 'dataset_raw',
                source: this.f_get_parse_data(res)//"time","Country","val"
              },
              ...datasetWithFilters
            ],
            animationDuration: 1000,
            title: {
              text: '月销售统计图'
            },
            tooltip: {
              order: 'valueDesc',
              trigger: 'axis'
            },
            xAxis: {
              type: 'category',
              nameLocation: 'middle'
            },
            yAxis: {
              name: 'val'
            },
            grid: {
              right: 140
            },
            series: seriesList
          };
          this.myChart.clear()
          this.myChart.setOption(option, true);
        }
      }, {month: this.this_month})
    },
    f_get_parse_data(data_str) {//[名称,时间,成本,卖出价格]
      const parse_arr = [["time", "Country", "val"]]
      try {
        //格式化数据，过滤表头
        var sort_arr = data_str.trim().split("\n").map(line => line.split(",")).filter((r, i) => i > 0)
        //补齐当月空数据日
        const month_days = []
        var day = this.this_month.substr(0, 4) + "-" + this.this_month.substr(-2) + "-01"
        while (day.replace(/-/g, "").startsWith(this.this_month)) {
          month_days.push(["", day.replace(/-/g, "/"), 0, 0])
          day = new Date(new Date(day).getTime() + 24 * 60 * 60 * 1000).toJSON().split("T")[0]
        }
        //排序
        sort_arr = sort_arr.concat(month_days).sort((a, b) => {
          return a[1].replace(/\//g, "") - b[1].replace(/\//g, "")
        })

        //合并相同日期的金额
        for (var i = sort_arr.length - 2; i >= 0; i--) {
          if (sort_arr[i][1] == sort_arr[i + 1][1]) {
            sort_arr[i][2] = parseFloat(sort_arr[i][2]) + parseFloat(sort_arr[i + 1][2])
            sort_arr[i][3] = parseFloat(sort_arr[i][3]) + parseFloat(sort_arr[i + 1][3])
            sort_arr.splice(i + 1, 1)
          }
        }
        console.info("sort_arr", sort_arr)
        //每日金额统计累加
        sort_arr.map((line_arr, i) => {
          const day = line_arr[1]
          const buy = parseFloat(line_arr[2])
          const sell = parseFloat(line_arr[3])
          parse_arr.push([day, this.countries[0], i == 0 ? buy : parse_arr[i * 3 - 2][2] + buy])
          parse_arr.push([day, this.countries[1], i == 0 ? sell : parse_arr[i * 3 - 1][2] + sell])
          parse_arr.push([day, this.countries[2], i == 0 ? (sell > 0 ? sell - buy : 0) : (parse_arr[i * 3][2] + (sell - buy))])
        })
        console.info("parse_arr", parse_arr)
        return parse_arr
      } catch (e) {
        console.error(e)
        return parse_arr
      }
    },
    f_query(url, callback, params = {}, qtype = "get") {
      qtype = qtype.toLowerCase()
      if (qtype == "get") {
        params = {params: params}
      }
      const axios = require("axios")
      axios[qtype](url, params).then(resp => {
        try {
          console.info(resp)
          callback(resp.status == 200, resp.data)
        } catch (e) {
          console.error(e)
          callback(0)
        }
      }).catch(e => console.error(e))
    },
    f_init_trend(_rawData) {
      const echarts = require("echarts")
      this.myChart = echarts.init(document.getElementById('i_trend'))
      this.myChart.setOption({})
    }
  }
}
</script>

<style>
.c_t_conter {
  width: 100%;
  height: 100%;
}

#i_trend {
  width: 100%;
  height: 100%;
}

.c_t_tools {
  position: absolute;
  top: 0;
  right: 0;
}

.c_t_months, .c_t_back {
  min-height: 50px;
  float: right;
  margin-right: 20px;
}
</style>
