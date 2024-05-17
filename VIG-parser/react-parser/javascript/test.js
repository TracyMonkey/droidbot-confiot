var RootStack = (0, _reactNavigation.createStackNavigator)({
    App: _index.default,
    HAND: _handModel.default,
    Setting: _setting.default,
    MoreSetting: _CommonSetting.MoreSetting,
    FirmwareUpgrade: _CommonSetting.FirmwareUpgrade
}, {
    initialRouteName: 'App',
    navigationOptions: function navigationOptions(_ref) {
        var navigation = _ref.navigation;
        return {
            headerMode: 'none',
            header: null
        };
    }
});
