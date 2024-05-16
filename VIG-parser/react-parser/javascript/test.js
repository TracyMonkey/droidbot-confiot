
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



