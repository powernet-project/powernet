let dashboard = {};

$(document).ready(function(ns) {
    const onLoad = function() {
        $('a .nav-link').removeClass('active');
        $('#nav-link-dashboard').addClass('active');
        $('#view-ecobee-chart-btn').on('click', startDataInterval);
    };

    let startDataInterval = function() {
        // build the plot chart
        displayChart();
        // get the initial data set
        requestEcobeeData();
        // set the interval into which we'll update the plot
        window.setInterval(requestEcobeeData, 30000);
    };

    let requestEcobeeData = function() {
        $.ajax({
            url: '/api/v1/ecobee_data',
            type: "GET",
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', 'Token ' + window.localStorage.getItem('token'));
            },
            success: function (data) {
                console.log(data);
                let actualTemp = data['runtime']['actualTemperature'] / 10,
                    actualTime = data['thermostatTime'];
                Plotly.extendTraces('ecobee-chart', {y: [[actualTemp]], x:[[actualTime]]}, [0]);
            }
        });
    };

    let displayChart = function() {
        let plotData = [{ x: [], y: [], type: 'scatter' }];
        Plotly.newPlot('ecobee-chart', plotData);
    };

    onLoad();
}(dashboard));