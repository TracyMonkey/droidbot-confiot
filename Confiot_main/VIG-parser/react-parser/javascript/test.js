
var RootStack = (0, _reactNavigation.createStackNavigator)({
    SettingPage: _ProjectAdapter.default.isYunmi ? SettingPage.SettingPage : SettingPage.MiSettingPage,
}, {
    initialRouteName: "MainPage",
    navigationOptions: function navigationOptions(_ref) {
        var navigation = _ref.navigation;
        return {
            header: _react.default.createElement(_NavigationBar.NavigationBar, {
                title: navigation.state.params ? navigation.state.params.title : "",
                left: [{
                    source: _NavigationBar.NavigationBar.ICON.BACK,
                    onPress: function onPress() {
                        navigation.goBack();
                    }
                }]
            })
        };
    }
});
