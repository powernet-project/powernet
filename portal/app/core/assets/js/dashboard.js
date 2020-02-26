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

        _setTemp(selectedTemp);
        _setMode(selectedMode);
    };

    let _setTemp = function(temp) {
        console.log('setting temp to ', temp)
        $.ajax({
            url: '/api/v1/ecobee/temperature/' + (temp + 30), // this offset is on purpose
            type: "POST",
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', 'Token ' + window.localStorage.getItem('token'));
            },
            success: function (data) {
                console.log('Setting ecobee temp', data);
            }
        });
    };

    let _setMode = function(mode) {
        console.log('setting mode to ', mode)
        $.ajax({
            url: '/api/v1/ecobee/mode/' + mode,
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
                    targetTemp = data['events'].length > 0 ? (data['events'][0]['heatHoldTemp'] / 10) - 3 : actualTemp,
                    actualTime = data['thermostatTime'],
                    hvacMode = data['settings']['hvacMode'];

                // if the actual temp, minus the 30 offset, is equal to or greater than the heatHoldTemp,
                // let's turn the hvac to off.
                if(data['runtime']['actualTemperature'] >= (data['events'][0]['heatHoldTemp'] - 30)) {
                    console.log('Turning the ecobee off since the actual temp is equal to or greater than the heat hold temp');
                    _setMode('off')
                }

                Plotly.extendTraces('ecobee-chart', {
                    y: [[actualTemp], [targetTemp], [hvacMode]],
                    x:[[actualTime], [actualTime], [actualTime]]
                }, [0, 1, 2]);
            }
        });
    };

    let displayChart = function() {
        let temperatureTrace = { x: [], y: [], type: 'scatter', name: 'Temperature' },
            targetTempTrace = { x: [], y: [], type: 'scatter', name: 'Target Temp' },
            hvacModeTrace = { x: [],  y: [], type: 'scatter', name: 'HVAC Mode', yaxis: 'y2' },
            plotData = [temperatureTrace, targetTempTrace, hvacModeTrace],
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