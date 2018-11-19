var consumption = consumption || {};

$(document).ready(function(ns) {
    const onLoad = function() {
        // get the homes device list
        $.ajax({
            url: '/api/v1/rms/consumption/?home_id=1',
            type: "GET",
            beforeSend: function(xhr){
                xhr.setRequestHeader('Authorization', 'Token ' + window.localStorage.getItem('token'));
            },
            success: function(data) {
                console.warn(data);
            }
        });
    };



    onLoad();
}(consumption));