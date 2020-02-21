let dashboard = {};

$(document).ready(function(ns) {
    const onLoad = function() {
        $('a .nav-link').removeClass('active');
        $('#nav-link-dashboard').addClass('active');
        $('#view-ecobee-chart-btn').on('click', startDataInterval);
        $('#set-ecobee-temp-mode-params').on('click', setTempMode);

        // create dropdown options for the temperature
        let drpdTemp = $('#ecobee-temp'),
            tempOptions = '';

        for(let i = 80; i >= 60; i--) {
            tempOptions += '<option value="' + (i * 10) + '">' + i + 'ºF</option>'
        }

        drpdTemp.append(tempOptions);
    };

    let setTempMode = function() {
        let selectedTemp = $('#ecobee-temp').val(),
            selectedMode = $('#ecobee-hvac-mode').val();

        console.log(selectedMode, selectedTemp);

        $.ajax({
            url: '/api/v1/ecobee/temperature/' + selectedTemp,
            type: "POST",
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', 'Token ' + window.localStorage.getItem('token'));
            },
            success: function (data) {
                console.log('Setting ecobee temp', data);
            }
        });

        $.ajax({
            url: '/api/v1/ecobee/mode/' + selectedMode,
            type: "POST",
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', 'Token ' + window.localStorage.getItem('token'));
            },
            success: function (data) {
                console.log('Setting ecobee mode', data);
            }
        });
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
            url: '/api/v1/ecobee/data',
            type: "GET",
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', 'Token ' + window.localStorage.getItem('token'));
            },
            success: function (data) {
                console.log(data);
                let actualTemp = data['runtime']['actualTemperature'] / 10,
                    actualTime = data['thermostatTime'],
                    hvacMode = data['settings']['hvacMode'];
                Plotly.extendTraces('ecobee-chart', {y: [[actualTemp], [hvacMode]], x:[[actualTime], [actualTime]]}, [0, 1]);
            }
        });
    };

    let displayChart = function() {
        let temperatureTrace = { x: [], y: [], type: 'scatter', name: 'Temperature' },
            hvacModeTrace = { x: [],  y: [], type: 'scatter', name: 'HVAC Mode', yaxis: 'y2' },
            plotData = [temperatureTrace, hvacModeTrace],
            layout = {
                title: 'Ecobee Temperature/Mode',
                yaxis: { title: 'Temp ºF' },
                yaxis2: {
                    title: 'HVAC Mode',
                    titlefont: { color: 'rgb(148, 103, 189)' },
                    tickfont: { color: 'rgb(148, 103, 189)' },
                    overlaying: 'y',
                    side: 'right'
                }
            };

        Plotly.newPlot('ecobee-chart', plotData, layout);
    };

    onLoad();
}(dashboard));