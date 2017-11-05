var demo3 = demo3 || {};

$(document).ready(function(ns) {
    var onLoad = function() {
        // setup on click listeners for the buttons
        setupClickListeners();
    },

    totalConsumptionValue = 0, ac5 = 0, fridge10 = 0, stove12 = 0, washer13 = 0, dishWasher14 = 0,

    setupClickListeners = function(){
        $('#stove-on-btn').on('click', function() {
            $.ajax({
                url: '/api/v1/device/12/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'ON', name: 'Stove_Oven_Exhaust_1', type: 'STOVE_OVEN_EXHAUST'})
            });
        });
        $('#stove-off-btn').on('click', function() {
            $.ajax({
                url: '/api/v1/device/12/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'OFF', name: 'Stove_Oven_Exhaust_1', type: 'STOVE_OVEN_EXHAUST'})
            });
        });
        $('#fridge-on-btn').on('click', function() {
            $.ajax({
                url: '/api/v1/device/10/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'ON', name: 'Refrigerator_1', type: 'REFRIGERATOR'})
            });
        });
        $('#fridge-off-btn').on('click', function() {
            $.ajax({
                url: '/api/v1/device/10/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'OFF', name: 'Refrigerator_1', type: 'REFRIGERATOR'})
            });
        });
        $('#washer-on-btn').on('click', function() {
            $.ajax({
                url: '/api/v1/device/13/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'ON', name: 'C_Washer_1', type: 'CLOTHES_WASHER'})
            });
        });
        $('#washer-off-btn').on('click', function() {
            $.ajax({
                url: '/api/v1/device/13/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'OFF', name: 'C_Washer_1', type: 'CLOTHES_WASHER'})
            });
        });
        $('#dishwasher-on-btn').on('click', function() {
            $.ajax({
                url: '/api/v1/device/14/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'ON', name: 'Dish_Washer', type: 'DISH_WASHER'})
            });
        });
        $('#dishwasher-off-btn').on('click', function() {
            $.ajax({
                url: '/api/v1/device/14/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'OFF', name: 'Dish_Washer', type: 'DISH_WASHER'})
            });
        });
        // $('#ac-on-btn').on('click', function() {
        //     $.ajax({
        //         url: '/api/v1/device/5/',
        //         dataType: 'json',
        //         contentType: 'application/json',
        //         type: 'PUT',
        //         data: JSON.stringify({status: 'ON', name: 'AC_1', type: 'AIR_CONDITIONER'})
        //     });
        // });
        // $('#ac-off-btn').on('click', function() {
        //     $.ajax({
        //         url: '/api/v1/device/5/',
        //         dataType: 'json',
        //         contentType: 'application/json',
        //         type: 'PUT',
        //         data: JSON.stringify({status: 'OFF', name: 'AC_1', type: 'AIR_CONDITIONER'})
        //     });
        // });


        // setup listeners for tapareas
        $('#gwd-taparea_oven').on('click', function() {
            $.get('/api/v1/rms/consumption?id=12', function(data) {
                stove12 = data['result'] * 120;
                stove12 = Math.round(stove12 * 10) / 10;
                $('#stove-12').text(stove12.toString());
            });
        });
        $('#gwd-taparea_dishwasher').on('click', function() {
            $.get('/api/v1/rms/consumption?id=14', function(data) {
                dishWasher14 = data['result'] * 120;
                dishWasher14 = Math.round(dishWasher14 * 10) / 10;
                $('#dish-washer-14').text(dishWasher14.toString());
            });
        });
        $('#gwd-taparea_fridge').on('click', function() {
            $.get('/api/v1/rms/consumption?id=10', function(data) {
                fridge10 = data['result'] * 120;
                fridge10 = Math.round(fridge10 * 10) / 10;
                $('#fridge-10').text(fridge10.toString());
            });
        });
        $('#gwd-taparea-laundry').on('click', function() {
            $.get('/api/v1/rms/consumption?id=13', function(data) {
                washer13 = data['result'] * 120;
                washer13 = Math.round(washer13 * 10) / 10;
                $('#washer-13').text(washer13.toString());
            });
        });

        $('#gwd-taparea_3').on('click', this.getDevicesState);
    };

    ns.getDevicesState = function() {
        $.get('/api/v1/device', function(data) {
            var devices = data['results'];
            for (var i = 0; i < devices.length; i++) {
                // all devices default to OFF on the UI, so we only really need to handle ON
                if (devices[i]['status'] === 'ON') {
                    if (devices[i]['id'] === 10) {
                        $('#fridge-on-btn').click();
                    } else if (devices[i]['id'] === 12) {
                        $('#stove-on-btn').click();
                    } else if (devices[i]['id'] === 13) {
                        $('#washer-on-btn').click();
                    } else if (devices[i]['id'] === 14) {
                        $('#dishwasher-on-btn').click();
                    }
                }
            }
        });
    };

    ns.loadTotalConsumption = function() {
        // zero out the existing total consumption
        totalConsumptionValue = 0;

        var pwrnetApiUrl = '/api/v1/rms/consumption?id=',
            deviceIds = [5, 10, 12, 13, 14];

        for (var i = 0; i < deviceIds.length; i++) {
            $.get(pwrnetApiUrl + deviceIds[i].toString(), function(data) {
                totalConsumptionValue += (data['result'] * 120);
                $('#pwr-consumption-value').text(Math.round(totalConsumptionValue * 10) / 10);
            });
        }
    };

    ns.loadPvStatus = function() {
        var enphaseUrl = 'https://api.enphaseenergy.com/api/v2/systems/1308698/summary',
            queryParams = '?datetime_format=iso8601',
            apiKeyPanelOne = '&user_id=4f546b334d6a63770a&key=4231da82ac549ee9c197071dcbc857ae';

        $.get(enphaseUrl + queryParams + apiKeyPanelOne, function(data) {
            $('#solar-gen-value').text(data['current_power']);
        });
    };

    ns.loadWeatherData = function() {
        var url = "http://api.openweathermap.org/data/2.5/weather?zip=94305,us&APPID=6faafe3de999509b86b118803ee2ca8f&units=imperial";
        $.get(url, function(data) {
            $('#weather-value').text(data['main']['temp']);
        });
    };

    onLoad();
}(demo3));