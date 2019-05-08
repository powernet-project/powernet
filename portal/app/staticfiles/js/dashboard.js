let dashboard = {};

$(document).ready(function(ns) {
    const onLoad = function() {
        $('a .nav-link').removeClass('active');
        $('#nav-link-dashboard').addClass('active');
    };

    onLoad();
}(dashboard));