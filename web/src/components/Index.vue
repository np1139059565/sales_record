<template src="../html/index.html"></template>
<script>
export default {
    data() {
        return {
            isDragging: false,
            dragStartX: 0,
            dragStartY: 0,
            modalStartX: 0,
            modalStartY: 0,
            modalTop: 0,
            modalLeft: 0,
            // 已保存的手机信息[{device,label,hand_nodes}]
            d_phones: [],
            // 在线的驱动列表[{label,value}]
            d_devices: [],
            // 已选驱动信息
            d_selected_device: { label: '', value: '' },
            // 操作列表
            d_hand_nodes: [],
            // 默认操作列表
            d_def_hand_nodes: [
                { label: '搜索按钮', type: 'search_open', hand_type: 'click', class: '', bounds: '', 'resource-id': '' },
                { label: '搜索输入', type: 'search_input', hand_type: 'input', class: '', value: '', 'resource-id': '' },
                { label: '搜索确认', type: 'search_ok', hand_type: 'click', class: '', bounds: '', 'resource-id': '' },
                { label: '查找', type: 'check', hand_type: 'check', class: '', 'resource-id': '', text: '' },
                { label: '滑动', type: 'slice', hand_type: 'slice', bounds: '', speed: 0.2 }
            ],
            // 当前页面信息
            d_dump_nodes: [],
            // 默认滑动速度
            d_def_speeds: [0.2, 0.4, 0.8],
            d_dialog_title: '',
            d_is_show_start_button: false,
            d_pobj_arr: [],
            d_is_auto_refush_pobj: false,
            d_pobj_refush_id: -1,
            d_pobj_bottom_page: -1
        };
    },
    mounted() {
        // refush devices
        this.f_refush_phones();
        // auto refush pobj
        this.d_pobj_refush_id = setInterval(() => {
            this.f_refush_pobj('last', (code, conter) => {
                if (code) {
                    if (this.d_pobj_bottom_page < 0) {
                        this.d_pobj_bottom_page = conter.index;
                    }
                    const new_pobj_arr = JSON.parse(conter.conter)
                        .filter(p => this.d_pobj_arr.length == 0 || p.time > this.d_pobj_arr[0].time)
                        .sort((p1, p2) => p2.time - p1.time);
                    if (new_pobj_arr.length > 0) {
                        //var url = "https://fanyi.baidu.com/gettts?lan=zh&text="+encodeURI(str)+"&spd=5&source=web"
                        //this.d_audio = "/static/audio/11981.mp3"
                        this.$refs.audio1.play();
                        this.d_pobj_arr = new_pobj_arr.concat(this.d_pobj_arr);
                    }
                }
            });
        }, 1000);
        // 监听滚动事件
        window.addEventListener('scroll', () => {
            // 获取滚动条的位置
            const scrollHeight = document.documentElement.scrollHeight;
            const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
            const clientHeight = document.documentElement.clientHeight;
            console.info(scrollHeight, scrollTop, clientHeight)
            // 判断滚动条是否滚动到了页面底部
            if (scrollTop + clientHeight + 5 >= scrollHeight) {
                // 执行数据刷新操作
                this.f_pobj_next()
            }
        });
    },
    methods: {
        f_start_by_wifi() {
            this.f_query_only('/py/flask_server/f_start_by_wifi',
                (code, msg) => {
                    // 将字符串转换为十六进制字符串
                    const hand_nodes_str = JSON.stringify(this.d_hand_nodes);
                    const encoder = new TextEncoder();
                    const data = encoder.encode(hand_nodes_str);
                    const hex_str = Array.from(data, byte => byte.toString(16).padStart(2, '0')).join('');
                    const hex_str_with_dashes = hex_str.match(/.{1,2}/g).join('-');

                    const script_str = msg + 'main(server_ip="192.168.1.37",input_value_length='
                        + this.d_hand_nodes.filter(t => t['type'] == 'search_input')[0].value.split('@').length
                        + ',atx_ip="127.0.0.1' //+ this.d_selected_device.value.trim().split(':')[0].trim()
                        + '",encode_str="' + hex_str_with_dashes + '")';


                    // 创建一个临时的textarea元素
                    const textarea = document.createElement('textarea');
                    // 设置要复制的文本内容
                    textarea.value = script_str;
                    // 将textarea元素添加到页面中
                    document.body.appendChild(textarea);
                    // 选择textarea中的文本
                    textarea.select();
                    // 执行复制操作
                    document.execCommand('copy');
                    // 移除临时的textarea元素
                    document.body.removeChild(textarea);
                    alert('已经将脚本发送到你的剪切板中,请直接在qpython中新建文件启动即可！');
                });
        },
        f_pobj_next() {
            if (this.d_pobj_bottom_page > 0) {
                this.f_refush_pobj(this.d_pobj_bottom_page -= 1, (code, conter) => {
                    if (code) {
                        this.d_pobj_arr.push(...JSON.parse(conter.conter));
                    }
                });
            }
        },
        f_timestamp_to_str(timestamp) {
            // 获取当前时间戳
            // var timestamp = 1688581598.2155583;

            // 创建一个Date对象
            var date = new Date(timestamp * 1000);

            // 获取年、月、日、时、分、秒
            var year = date.getFullYear();
            var month = ('0' + (date.getMonth() + 1)).slice(-2);
            var day = ('0' + date.getDate()).slice(-2);
            var hours = ('0' + date.getHours()).slice(-2);
            var minutes = ('0' + date.getMinutes()).slice(-2);
            var seconds = ('0' + date.getSeconds()).slice(-2);

            // 格式化为年月日时分秒
            return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;

        },
        f_pstrhex_to_str(pstrhex) {
            let byteArray = [];
            for (let i = 0; i < pstrhex.length; i += 2) {
                const byte = parseInt(pstrhex.substr(i, 2), 16);
                byteArray.push(byte);
            }

            const decodedString = new TextDecoder('utf-8').decode(Uint8Array.from(byteArray));
            return decodedString;
        },
        getComponentType(i,timestamp) {
            var hindex=i+1;
            if(this.d_pobj_arr.length>i+1&&this.d_pobj_arr[0].time-timestamp<30){
                hindex=1;
            }
            return hindex >= 0 && hindex < 3 ? 'h' + hindex: 'h5';
        },

        f_refush_pobj(i, callback) {
            if (this.d_is_auto_refush_pobj || i >= 0) {
                this.f_query('/py/flask_server/get_pstr?page=' + (i >= 0 ? i : 'last'),
                    (code, msg) => {
                        if (typeof (callback) == 'function') {
                            callback(code, msg)
                        }
                    });
            }
        },
        f_del_device(p) {
            // 弹出确认框
            const rbool = confirm("你确定要执行此操作吗？");
            if (rbool) {
                this.f_query_only('/py/flask_server/f_phone_delete?device=' + p.device,
                    (code, msg) => {
                        alert(msg)
                        this.f_refush_phones()
                    });
            }
        },
        f_start_phone() {
            const nodes = this.d_hand_nodes;
            console.info('start phone', this.d_hand_nodes);
            this.f_query_only('/py/flask_server/f_phone_start?device=' + this.d_selected_device.value
                + '&hand_nodes=' + JSON.stringify(nodes) + '&ivlen=' + nodes.filter(t => t['type'] == 'search_input')[0].value.split('@').length,
                (code, msg) => {
                    alert(code + ':' + msg)
                });
        },
        f_test_hand_node(i) {
            const tdata = this.d_hand_nodes[i];
            console.info('test hand node', this.d_hand_nodes[i]);
            this.f_query_only('/py/get_ui_by_uiautomator2/' + tdata['hand_type'] + '?device=' + this.d_selected_device.value
                + '&node_info=' + JSON.stringify(tdata),
                (code, msg) => {
                    alert(code + ':' + msg)
                });
        },
        f_save_phone() {
            this.f_query_only('/py/flask_server/f_save_phone?phone_info=' + JSON.stringify({
                label: this.d_selected_device.label,
                hand_nodes: this.d_hand_nodes,
                device: this.d_selected_device.value
            }),
                (code, msg) => {
                    alert(msg)
                    if (msg == 'success') {
                        this.f_refush_phones(() => {
                            this.f_refush_devices(null, true);
                        });
                    }
                });
        },
        f_change_node1(e) {
            console.info('f_change_node1', e.target.getAttribute('selected_node_index'), e.target.value);
            this.d_hand_nodes[e.target.getAttribute('selected_node_index')] = JSON.parse(e.target.value);
        },
        f_change_node2(e) {
            console.info('f_change_node2', e.target.getAttribute('selected_node_index'), e.target.selectedIndex);
            const keys = Object.keys(this.d_hand_nodes[e.target.getAttribute('selected_node_index')]);
            keys.map(k => {
                if (this.d_dump_nodes[e.target.selectedIndex][k] != null)
                    this.d_hand_nodes[e.target.getAttribute('selected_node_index')][k] = this.d_dump_nodes[e.target.selectedIndex][k];
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
        f_refush_dump_nodes(callback) {
            //refush dump nodes
            this.f_query_only("/py/get_ui_by_uiautomator2/dump?device=" + this.d_selected_device.value, (code, msg) => {
                if (code) {
                    this.d_dump_nodes = [];
                    var parser = new DOMParser();
                    var xmlDoc = parser.parseFromString(msg, "text/xml");
                    var nodes = this.f_get_all_last_node(xmlDoc);

                    for (var i = 0; i < nodes.length; i++) {
                        var text = nodes[i].getAttribute("text");
                        if (text.trim().length == 0) {
                            text = nodes[i].getAttribute("content-desc");
                        }
                        const node = {};
                        const attrs = nodes[i].attributes;
                        for (var j = 0; j < attrs.length; j++) {
                            node[attrs[j].name] = attrs[j].value;
                        }
                        this.d_dump_nodes.push(node);
                    }

                } else {
                    alert(msg)
                }
                if (typeof (callback) == 'function') {
                    callback(code)
                }
            });
        },
        f_refush_phones(callback) {
            this.f_refush_devices(() => {
                this.f_query("/py/flask_server/f_get_phones", (code, phones) => {
                    try {
                        if (code) {
                            console.info("get phones", phones)
                            this.d_phones = phones
                                .map(p => {
                                    //颜色标记
                                    p.style = ("cursor:pointer;margin-right:5px;border:0;background-color:" + (this.d_devices.filter(d => p.device == d.value).length == 0 ? "yellow" : "green"));
                                    return p;
                                });
                        }
                        if (callback != null) {
                            callback(code);
                        }
                    } catch (e) {
                        console.error(e)
                    }
                });
            });
        },
        f_refush_devices(callback, isFindLabel = false) {
            this.f_query_only("/py/adb/devices", (code, msg) => {
                if (code) {
                    this.d_devices = msg.split("\r\n").filter((v, i) => i > 0)
                        .map(line => line.split("\t")[0].split(":")[0])
                        .map(d => {
                            return {
                                value: d,
                                label: isFindLabel ? this.d_phones.filter(p => p.device == d).map(p => p.label).concat(d)[0] : d
                            }
                        });
                } else {
                    alert(msg);
                }
                if (callback != null) {
                    callback(code);
                }
            });
        },
        f_close_dialog() {
            this.$refs.dialog.style.display = 'none';
        },
        f_show_dialog(device, title = '添加手机', isShowStartButton = false) {
            this.d_dialog_title = title;
            this.d_is_show_start_button = isShowStartButton;
            this.$refs.dialog.style.display = 'block';
            // refush devices
            this.f_refush_devices(() => {
                if (typeof device == 'object' && device.value != null) {
                    this.d_selected_device = device;
                } else {
                    this.d_selected_device = this.d_devices[0];
                }
                // refush dump nodes
                this.f_refush_dump_nodes(() => {
                    // refush hand nodes by selected device
                    this.d_hand_nodes = [];
                    // is saved device
                    this.d_phones.map(p => {
                        if (p.device == this.d_selected_device.value) {
                            this.d_hand_nodes = p.hand_nodes;
                        }
                    });

                    // is new device
                    if (this.d_hand_nodes.length == 0) {
                        this.d_hand_nodes = this.d_def_hand_nodes.map(n => {
                            Object.keys(n).map(k => {
                                if (this.d_dump_nodes[0][k] != null)
                                    n[k] = this.d_dump_nodes[0][k];
                            });
                            return n;
                        });
                    }
                });
            }, true);
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
                    if (e && e.response && e.response.status == 500) {
                        callback(false, e.response.data)
                    } else console.error(e)
                })
        },
        startDrag(event) {
            this.isDragging = true;
            this.dragStartX = event.clientX;
            this.dragStartY = event.clientY;
            this.modalStartX = this.modalLeft;
            this.modalStartY = this.modalTop;

            document.addEventListener("mousemove", this.handleDrag);
            document.addEventListener("mouseup", this.stopDrag);
        },
        handleDrag(event) {
            if (this.isDragging) {
                const offsetX = event.clientX - this.dragStartX;
                const offsetY = event.clientY - this.dragStartY;
                this.modalLeft = this.modalStartX + offsetX;
                this.modalTop = this.modalStartY + offsetY;
            }
        },
        stopDrag() {
            this.isDragging = false;
            document.removeEventListener("mousemove", this.handleDrag);
            document.removeEventListener("mouseup", this.stopDrag);
        }
    }
};
</script>
<style src="../css/index.css"></style>