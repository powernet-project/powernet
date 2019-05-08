let settings = {};

$(document).ready(function(ns) {
    const onLoad = function() {
        $('a .nav-link').removeClass('active');
        $('#nav-link-settings').addClass('active');

        getHomeData();
        getUserData();
    };

    const getHomeData = () => {
        $.ajax({
            url: `/api/v1/home/`,
            type: 'GET',
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', 'Token ' + window.localStorage.getItem('token'));
            },
            success: (data) => {
                $('#home-data').html(JSON.stringify(data, null, '\t'));
            }
        });
    };

    const getUserData = () => {
        $.ajax({
            url: `/api/v1/powernet_user/`,
            type: 'GET',
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', 'Token ' + window.localStorage.getItem('token'));
            },
            success: (data) => {
                $('#user-data').html(JSON.stringify(data, null, '\t'));
            }
        });
    };

    onLoad();
}(settings));