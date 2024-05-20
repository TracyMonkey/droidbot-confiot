__d(function (global, _$$_REQUIRE, _$$_IMPORT_DEFAULT, _$$_IMPORT_ALL, module, exports, _dependencyMap) {
    'use strict';

    var _interopRequireDefault = _$$_REQUIRE(_dependencyMap[0]);

    Object.defineProperty(exports, "__esModule", {
        value: true
    });
    exports.default = undefined;

    var _classCallCheck2 = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[1]));

    var _createClass2 = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[2]));

    var _possibleConstructorReturn2 = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[3]));

    var _getPrototypeOf2 = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[4]));

    var _inherits2 = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[5]));

    var _miot = _$$_REQUIRE(_dependencyMap[6]);

    var _TitleBar = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[7]));

    var _Card = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[8]));

    var _Switch = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[9]));

    var _MessageDialog = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[10]));

    var _LoadingDialog = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[11]));

    var _Separator = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[12]));

    var _react = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[13]));

    var _ListItemWithSwitch = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[14]));

    var _reactNative = _$$_REQUIRE(_dependencyMap[15]);

    var _reactNativeRootToast = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[16]));

    var _CommonUtils = _interopRequireDefault(_$$_REQUIRE(_dependencyMap[17]));

    var selectedRepeatTextArray = ["执行一次", "每天", "周一至周五"];
    var selectedRepeatDayTextArray = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"];

    var deviceId = _miot.Device.deviceID.replace("miwifi.", "");

    var url = '/appgateway/third/miwifi/app/r/api/xqsmarthome/request_smartcontroller';

    var HealthMode = function (_React$Component) {
        (0, _inherits2.default)(HealthMode, _React$Component);

        function HealthMode(props) {
            var _this;

            (0, _classCallCheck2.default)(this, HealthMode);
            _this = (0, _possibleConstructorReturn2.default)(this, (0, _getPrototypeOf2.default)(HealthMode).call(this, props));

            _this._createMenuData();

            _this.state = {
                dataSource: new _reactNative.ListView.DataSource({
                    rowHasChanged: function rowHasChanged(r1, r2) {
                        return r1 !== r2;
                    }
                }),
                list: [],
                visible1: false,
                visible2: false
            };
            return _this;
        }

        (0, _createClass2.default)(HealthMode, [{
            key: "_createMenuData",
            value: function _createMenuData() {
                var device = this.props.navigation.getParam('param') || {};
                this._menuData = [];
            }
        }, {
            key: "_openSubPage",
            value: function _openSubPage(page, props) {
                this.props.navigation.navigate(page, props);
            }
        }, {
            key: "_generateID",
            value: function _generateID() {
                var idList = [];
                this.state.list.map(function (v, i) {
                    idList.push(v.id);
                });
                var arr1 = [30000, 30001, 30002, 30003, 30004, 30005, 30006, 30007, 30008, 30009];
                var arr2 = [].concat(arr1).filter(function (x) {
                    return [].concat(idList).every(function (y) {
                        return y !== x;
                    });
                });
                return arr2[0];
            }
        }, {
            key: "_openTimeSetting",
            value: function _openTimeSetting() {
                var _this2 = this;

                if (this.state.list.length >= 9) {
                    _reactNativeRootToast.default.show("小米WiFi：最多只能添加9个定时哦~");

                    return;
                }

                this.props.navigation.navigate("TimeSetting", {
                    type: 'add',
                    callback: function callback(item) {
                        item.id = _this2._generateID();
                        item.enabled = true;
                        var repeat;

                        var duration = _this2._calDurationTime(item.selectedWifiCloseRawString, item.selectedWifiOpenRawString);

                        if (item.selectedRepeatArray[0] == 0) {
                            repeat = 0;
                        } else if (item.selectedRepeatArray[0] == 1) {
                            repeat = '0,1,2,3,4,5,6';
                        } else if (item.selectedRepeatArray[0] == 2) {
                            repeat = '1,2,3,4,5';
                        } else {
                            repeat = item.selectedIndexArray1.map(function (v) {
                                if (v == 6) {
                                    return v = 0;
                                } else {
                                    return v = v + 1;
                                }
                            }).toString();
                        }

                        var data = _this2._generateXHRData({
                            id: item.id,
                            command: "scene_setting",
                            enabled: true,
                            repeat: repeat,
                            time: item.selectedWifiCloseRawString + ':00',
                            duration: duration
                        });

                        var payload = JSON.stringify(data);
                        var method = 'POST';
                        var paramsDic = {
                            method: method,
                            params: {
                                deviceId: deviceId,
                                payload: payload
                            }
                        };

                        _miot.Service.callSmartHomeAPI(url, paramsDic).then(function (res) {
                            if (res.code == 0) {
                                _this2.setState(function (prev) {
                                    list: prev.list.push(item);
                                }, function () {
                                    _this2.setState({
                                        dataSource: _this2.state.dataSource.cloneWithRows(_this2.state.list)
                                    });
                                });
                            }

                            _CommonUtils.default.ShowToastBottom('数据添加成功');
                        }).catch(function (e) {
                            _CommonUtils.default.ShowToastBottom('数据添加失败');
                        });
                    }
                });
            }
        }, {
            key: "_fetchListData",
            value: function _fetchListData() {
                var _this3 = this;

                this._recloneData();

                var payloadDic = {
                    command: 'get_multiple_scene_setting',
                    start_id: '30000',
                    end_id: '30009'
                };
                var payload = JSON.stringify(payloadDic);
                var method = 'GET';
                var paramsDic = {
                    method: method,
                    params: {
                        deviceId: deviceId,
                        payload: payload
                    }
                };

                _miot.Service.callSmartHomeAPI(url, paramsDic).then(function (res) {
                    if (res.code == 0) {
                        var newList = _this3._formatDataList(res.scene_list);

                        _this3.setState({
                            list: newList
                        }, function () {
                            _this3.setState({
                                dataSource: _this3.state.dataSource.cloneWithRows(_this3.state.list)
                            });
                        });
                    }

                    _CommonUtils.default.ShowToastBottom('数据读取成功');
                }).catch(function (e) {
                    _CommonUtils.default.ShowToastBottom('数据读取失败');

                    _this3.props.navigation.goBack();
                });
            }
        }, {
            key: "_formatDataList",
            value: function _formatDataList(origin) {
                var _this4 = this;

                var newList = [];
                origin.map(function (v, i) {
                    var id = v.id;

                    if (v.launch) {
                        var enabled = v.launch.timer.enabled;
                        var repeat = v.launch.timer.repeat;
                        var time = v.launch.timer.time;
                        var selectedWifiCloseRawString = time.substring(0, 5);
                        var selectedWifiCloseArray = selectedWifiCloseRawString.split(':');
                        var selectedRepeatArray = [];
                        var selectedIndexArray1 = [];
                        var selectedCustomArray = [];
                        var duration = v.action_list[0].extra.duration;

                        var selectedWifiOpenRawString = _this4._calEndTime(selectedWifiCloseArray, duration);

                        var selectedWifiOpenArray = selectedWifiOpenRawString.split(':');

                        if (repeat) {
                            if (repeat == '1,2,3,4,5') {
                                selectedRepeatArray = [2];
                                selectedIndexArray1 = selectedCustomArray = [0, 1, 2, 3, 4];
                            } else if (repeat == '0,1,2,3,4,5,6' || repeat == '1,2,3,4,5,6,0') {
                                selectedRepeatArray = [1];
                                selectedIndexArray1 = selectedCustomArray = [0, 1, 2, 3, 4, 5, 6];
                            } else {
                                selectedRepeatArray = [3];
                                repeat.split(',').map(function (v) {
                                    if (v == 0) {
                                        selectedIndexArray1.push(6);
                                    } else {
                                        selectedIndexArray1.push(v - 1);
                                    }
                                });
                                selectedCustomArray = selectedIndexArray1;
                            }
                        } else {
                            selectedRepeatArray = [0];
                            selectedIndexArray1 = [];
                            selectedCustomArray = [5, 6];
                        }

                        newList.push({
                            id: id,
                            selectedWifiCloseRawString: selectedWifiCloseRawString,
                            selectedWifiCloseArray: selectedWifiCloseArray,
                            selectedRepeatArray: selectedRepeatArray,
                            selectedIndexArray1: selectedIndexArray1,
                            selectedWifiOpenRawString: selectedWifiOpenRawString,
                            selectedCustomArray: selectedCustomArray,
                            selectedWifiOpenArray: selectedWifiOpenArray,
                            enabled: enabled,
                            duration: duration
                        });
                    } else {
                        newList.push({
                            id: id,
                            selectedWifiCloseRawString: '00:00',
                            selectedWifiCloseArray: ["00", "00"],
                            selectedRepeatArray: [0],
                            selectedIndexArray1: [0],
                            selectedWifiOpenRawString: '08:00',
                            selectedCustomArray: [],
                            selectedWifiOpenArray: ["08", "00"],
                            enabled: false,
                            duration: 28800000
                        });
                    }
                });
                return newList;
            }
        }, {
            key: "_calEndTime",
            value: function _calEndTime(startTimeArray, duration) {
                var startHour = startTimeArray[0];
                var startMinute = startTimeArray[1];
                var startMilliSecond = (Number(startHour * 3600) + Number(startMinute * 60)) * 1000;
                var endMilliSecond = startMilliSecond + duration;

                var endTime = this._secTotime(endMilliSecond);

                return endTime;
            }
        }, {
            key: "_calDurationTime",
            value: function _calDurationTime(startTime, endTime) {
                var startTimeArray = startTime.split(':');
                var endTimeArray = endTime.split(':');
                var startHour = startTimeArray[0];
                var startMinute = startTimeArray[1];
                var startMilliSecond = (Number(startHour * 3600) + Number(startMinute * 60)) * 1000;
                var endHour = endTimeArray[0];
                var endMinute = endTimeArray[1];
                var endMilliSecond = (Number(endHour * 3600) + Number(endMinute * 60)) * 1000;
                var duration = endMilliSecond - startMilliSecond;

                if (duration < 0) {
                    duration = duration + 86400;
                }

                return duration;
            }
        }, {
            key: "_secTotime",
            value: function _secTotime(s) {
                var t;
                s = s / 1000;

                if (s > -1) {
                    var hour = Math.floor(s / 3600);
                    var min = Math.floor(s / 60) % 60;
                    hour = hour >= 24 ? hour - 24 : hour;
                    min = min >= 60 ? min - 60 : min;

                    if (hour < 10) {
                        t = '0' + hour + ":";
                    } else {
                        t = hour + ":";
                    }

                    if (min < 10) {
                        t += "0";
                    }

                    t += min;
                }

                return t;
            }
        }, {
            key: "_recloneData",
            value: function _recloneData() {
                this.setState({
                    dataSource: this.state.dataSource.cloneWithRows(this.state.list)
                });
            }
        }, {
            key: "_editItem",
            value: function _editItem(rowData, sectionID, rowID) {
                var _this5 = this;

                this._openSubPage('TimeSetting', {
                    type: 'edit',
                    info: rowData,
                    callback: function callback(info) {
                        var repeat = info.selectedIndexArray1.map(function (v) {
                            if (v == 6) {
                                return v = 0;
                            } else {
                                return v = v + 1;
                            }
                        }).toString();

                        var duration = _this5._calDurationTime(info.selectedWifiCloseRawString, info.selectedWifiOpenRawString);

                        var data = _this5._generateXHRData({
                            id: info.id,
                            command: "scene_update",
                            enabled: info.enabled,
                            repeat: repeat,
                            time: info.selectedWifiCloseRawString + ':00',
                            duration: duration
                        });

                        var payload = JSON.stringify(data);
                        var method = 'POST';
                        var paramsDic = {
                            method: method,
                            params: {
                                deviceId: deviceId,
                                payload: payload
                            }
                        };

                        _miot.Service.callSmartHomeAPI(url, paramsDic).then(function (res) {
                            if (res.code == 0) {
                                var copyList = JSON.parse(JSON.stringify(_this5.state.list));
                                copyList.forEach(function (v, i) {
                                    if (v.id == param.rowData.id) {
                                        copyList[i] = item;
                                    }
                                });

                                _this5.setState(function (prev) {
                                    list: copyList;
                                }, function () {
                                    _this5.setState({
                                        dataSource: _this5.state.dataSource.cloneWithRows(_this5.state.list)
                                    });
                                });

                                _CommonUtils.default.ShowToastBottom('编辑成功');
                            }
                        }).catch(function (e) {
                            _CommonUtils.default.ShowToastBottom('编辑失败');
                        });
                    }
                });
            }
        }, {
            key: "showLoading",
            value: function showLoading() {
                this.setState({
                    visible2: true
                });
            }
        }, {
            key: "hideLoading",
            value: function hideLoading() {
                this.setState({
                    visible2: false
                });
            }
        }, {
            key: "getInnerView",
            value: function getInnerView(rowData) {
                var _this6 = this;

                var spellTitle = rowData.selectedWifiCloseRawString + '关闭Wi-Fi，' + rowData.selectedWifiOpenRawString + '开启Wi-Fi';
                var repeatSubtitle;

                if (selectedRepeatTextArray[rowData.selectedRepeatArray[0]]) {
                    repeatSubtitle = selectedRepeatTextArray[rowData.selectedRepeatArray[0]];
                } else {
                    repeatSubtitle = rowData.selectedIndexArray1.map(function (o) {
                        return selectedRepeatDayTextArray[o];
                    }).join(",");
                }

                return _react.default.createElement(_reactNative.View, {
                    style: styles.innerContainer
                }, _react.default.createElement(_reactNative.View, {
                    style: {
                        flex: 1
                    }
                }, _react.default.createElement(_reactNative.Text, {
                    style: styles.innerTitle,
                    numberOfLines: 1
                }, spellTitle), _react.default.createElement(_reactNative.Text, {
                    style: styles.innersubTitle,
                    numberOfLines: 1
                }, repeatSubtitle)), _react.default.createElement(_Switch.default, {
                    style: {
                        width: 60,
                        height: 30
                    },
                    onTintColor: "#2C7DFA",
                    tintColor: "#dedede",
                    value: rowData.enabled,
                    onValueChange: function onValueChange(value) {
                        _this6._switchChange(value, rowData);
                    }
                }), _react.default.createElement(_Separator.default, {
                    style: {
                        height: 0.5
                    }
                }));
            }
        }, {
            key: "_generateXHRData",
            value: function _generateXHRData(_ref) {
                var id = _ref.id,
                    command = _ref.command,
                    enabled = _ref.enabled,
                    duration = _ref.duration,
                    repeat = _ref.repeat,
                    time = _ref.time;
                var obj = {
                    "id": 30000,
                    "command": "scene_setting",
                    "name": "健康模式",
                    "action_list": [{
                        "block": 1,
                        "delay": 0,
                        "extra": {
                            "duration": 28800000,
                            "total_length": 0
                        },
                        "keyName": "健康模式",
                        "name": "小米路由器",
                        "thirdParty": "xmrouter",
                        "type": "normal_wifi_down"
                    }],
                    "launch": {
                        "timer": {
                            "enabled": true,
                            "time": "00:00:00",
                            "repeat": "1,2,3,4,5"
                        }
                    }
                };
                if (id) obj.id = id;
                if (command) obj.command = command;
                obj.launch.timer.enabled = enabled;
                if (time) obj.launch.timer.time = time;

                if (repeat) {
                    obj.launch.timer.repeat = repeat;
                } else {
                    delete obj.launch.timer.repeat;
                }

                if (duration) obj.action_list[0].extra.duration = duration;
                return obj;
            }
        }, {
            key: "_switchChange",
            value: function _switchChange(value, rowData) {
                var _this7 = this;

                rowData.enabled = value;

                var data = this._generateXHRData({
                    id: rowData.id,
                    command: "scene_update",
                    enabled: value,
                    duration: rowData.duration
                });

                this.showLoading();
                var payload = JSON.stringify(data);
                var method = 'POST';
                var paramsDic = {
                    method: method,
                    params: {
                        deviceId: deviceId,
                        payload: payload
                    }
                };

                _miot.Service.callSmartHomeAPI(url, paramsDic).then(function (res) {
                    _this7.hideLoading();

                    if (res.code == 0) { }
                }).catch(function (e) {
                    return undefined;
                });
            }
        }, {
            key: "_deleteItem",
            value: function _deleteItem() {
                var _this8 = this;

                var data = {
                    id: this.state.deleteItemId,
                    command: "scene_delete"
                };
                this.showLoading();
                var payload = JSON.stringify(data);
                var method = 'POST';
                var paramsDic = {
                    method: method,
                    params: {
                        deviceId: deviceId,
                        payload: payload
                    }
                };

                _miot.Service.callSmartHomeAPI(url, paramsDic).then(function (res) {
                    _this8.hideLoading();

                    if (res.code == 0) {
                        var copyList = _this8.state.list.filter(function (v, i) {
                            return v.id != _this8.state.deleteItemId;
                        });

                        _this8.setState({
                            list: copyList
                        }, function () {
                            _this8.setState({
                                dataSource: _this8.state.dataSource.cloneWithRows(_this8.state.list)
                            });
                        });
                    }
                }).catch(function (e) {
                    return undefined;
                });
            }
        }, {
            key: "_renderRow",
            value: function _renderRow(rowData, sectionID, rowID) {
                var _this9 = this;

                var spellTitle = rowData.selectedWifiCloseRawString + '关闭Wi-Fi，' + rowData.selectedWifiOpenRawString + '开启Wi-Fi';
                var repeatSubtitle;

                if (selectedRepeatTextArray[rowData.selectedRepeatArray[0]]) {
                    repeatSubtitle = selectedRepeatTextArray[rowData.selectedRepeatArray[0]];
                } else {
                    repeatSubtitle = rowData.selectedIndexArray1.map(function (o) {
                        return selectedRepeatDayTextArray[o];
                    }).join(",");
                }

                return _react.default.createElement(_reactNative.TouchableHighlight, {
                    style: [styles.touchStyle, {
                        width: '100%',
                        height: 65,
                        padding: 15,
                        justifyContent: 'center',
                        marginTop: 0,
                        borderBottomWidth: 1,
                        borderColor: '#eee'
                    }],
                    underlayColor: "rgba(0,0,0,.05)",
                    onPress: function onPress(_) {
                        _this9._editItem(rowData, sectionID, rowID);
                    },
                    onLongPress: function onLongPress(_) {
                        _this9.setState({
                            visible1: true,
                            deleteItemId: rowData.id
                        });
                    }
                }, _react.default.createElement(_reactNative.View, {
                    style: styles.innerContainer
                }, _react.default.createElement(_reactNative.View, {
                    style: {
                        flex: 1
                    }
                }, _react.default.createElement(_reactNative.Text, {
                    style: styles.innerTitle,
                    numberOfLines: 1
                }, spellTitle), _react.default.createElement(_reactNative.Text, {
                    style: styles.innersubTitle,
                    numberOfLines: 1
                }, repeatSubtitle)), _react.default.createElement(_Switch.default, {
                    style: {
                        width: 46,
                        height: 24
                    },
                    onTintColor: "#32BAC0",
                    tintColor: "#F0F0F0",
                    value: rowData.enabled,
                    onValueChange: function onValueChange(value) {
                        _this9._switchChange(value, rowData);
                    }
                }), _react.default.createElement(_Separator.default, {
                    style: {
                        height: 0.5
                    }
                })));
            }
        }, {
            key: "componentDidMount",
            value: function componentDidMount() { }
        }, {
            key: "componentWillMount",
            value: function componentWillMount() {
                var _this10 = this;

                this._gestureHandlers = {
                    onStartShouldSetResponder: function onStartShouldSetResponder() {
                        return true;
                    },
                    onMoveShouldSetResponder: function onMoveShouldSetResponder() {
                        return true;
                    },
                    onResponderGrant: function onResponderGrant() {
                        _this10.setState({
                            bg: 'red'
                        });
                    },
                    onResponderMove: function onResponderMove() { },
                    onResponderRelease: function onResponderRelease() {
                        _this10.setState({
                            bg: 'white'
                        });
                    }
                };

                this._fetchListData();
            }
        }, {
            key: "componentWillUnmount",
            value: function componentWillUnmount() { }
        }, {
            key: "render",
            value: function render() {
                var _this11 = this;

                return _react.default.createElement(_reactNative.View, {
                    style: styles.container
                }, _react.default.createElement(_reactNative.View, {
                    style: styles.header
                }, _react.default.createElement(_reactNative.Image, {
                    style: styles.icon,
                    source: _$$_REQUIRE(_dependencyMap[18])
                }), _react.default.createElement(_reactNative.Text, {
                    style: styles.titleText
                }, "\u5B9A\u65F6\u5173\u95EDWi-Fi\uFF0C\u907F\u514D\u71AC\u591C\u4E0A\u7F51\uFF0C\u5065\u5EB7\u751F\u6D3B\u6D3B")), _react.default.createElement(_reactNative.View, {
                    style: styles.listCont
                }, _react.default.createElement(_reactNative.ListView, {
                    style: styles.list,
                    dataSource: this.state.dataSource,
                    renderRow: this._renderRow.bind(this)
                })), _react.default.createElement(_reactNative.View, {
                    style: styles.addWrap
                }, _react.default.createElement(_Separator.default, null), _react.default.createElement(_reactNative.TouchableHighlight, {
                    underlayColor: "transparent",
                    onPress: function onPress(_) {
                        return _this11._openTimeSetting();
                    }
                }, _react.default.createElement(_reactNative.View, {
                    style: styles.addcont
                }, _react.default.createElement(_reactNative.Image, {
                    style: styles.addIcon,
                    resizeMode: "contain",
                    source: _$$_REQUIRE(_dependencyMap[19])
                }), _react.default.createElement(_reactNative.Text, {
                    style: styles.addText
                }, "\u6DFB\u52A0\u5B9A\u65F6")))), _react.default.createElement(_LoadingDialog.default, {
                    visible: this.state.visible2,
                    message: "\u6B63\u5728\u4FDD\u5B58\u8BBE\u7F6E",
                    timeout: 10000
                }), _react.default.createElement(_MessageDialog.default, {
                    visible: this.state.visible1,
                    message: '确认删除此定时？',
                    buttons: [{
                        text: '取消',
                        style: {
                            color: '#666666'
                        },
                        callback: function callback(_) {
                            _this11.setState({
                                visible1: false,
                                deleteItemId: null
                            });
                        }
                    }, {
                        text: '确定',
                        style: {
                            color: '#2C7DFA'
                        },
                        callback: function callback(_) {
                            _this11.setState({
                                visible1: false
                            });

                            _this11._deleteItem();
                        }
                    }],
                    onDismiss: function onDismiss(_) { }
                }));
            }
        }]);
        return HealthMode;
    }(_react.default.Component);

    exports.default = HealthMode;

    HealthMode.navigationOptions = function (_ref2) {
        var navigation = _ref2.navigation;
        return {
            header: _react.default.createElement(_reactNative.View, null, _react.default.createElement(_TitleBar.default, {
                type: "dark",
                title: '健康模式',
                onPressLeft: function onPressLeft() {
                    navigation.goBack();
                }
            }))
        };
    };

    var styles = _reactNative.StyleSheet.create({
        container: {
            backgroundColor: '#fff',
            flex: 1
        },
        icon: {
            width: 100,
            height: 100,
            margin: 40
        },
        listCont: {
            flex: 1
        },
        list: {
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 60
        },
        header: {
            backgroundColor: '#1a1b2a',
            alignItems: 'center',
            height: 280
        },
        innerContainer: {
            flexDirection: 'row',
            justifyContent: 'space-between',
            alignItems: 'center'
        },
        innerTitle: {
            color: '#000'
        },
        innersubTitle: {
            fontSize: 12
        },
        titleText: {
            color: '#rgba(255,255,255,.5)',
            margin: 20
        },
        addWrap: {
            position: 'absolute',
            bottom: 0,
            left: 6,
            right: 6
        },
        addcont: {
            alignItems: 'center',
            justifyContent: 'center',
            height: 60,
            marginTop: 10,
            marginBottom: 10
        },
        addIcon: {
            width: 40,
            height: 40
        },
        addText: {
            marginTop: 5
        },
        separator: {
            backgroundColor: '#000',
            marginTop: 20
        }
    });
}, 10007, [14305, 14320, 14323, 14371, 14377, 14386, 10074, 10284, 10368, 10347, 10743, 10740, 10332, 10297, 10344, 10033, 10010, 10037, 10040, 10043]);
