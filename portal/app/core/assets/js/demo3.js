var demo3 = demo3 || {};

$(document).ready(function(ns) {
    var onLoad = function() {
        // setup on click listeners for the buttons
        setupClickListeners();
    },

    totalConsumptionValue = 0, ac5 = 0, fridge10 = 0, stove12 = 0, washer13 = 0, dishWasher14 = 0,

    setupClickListeners = function() {
        $('#gwd-taparea_oven-ON').on('click', function() {
            $.ajax({
                url: '/api/v1/device/12/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'ON', name: 'Stove_Oven_Exhaust_1', type: 'STOVE_OVEN_EXHAUST', home: 1})
            });
        });
        $('#gwd-taparea_oven-OFF').on('click', function() {
            $.ajax({
                url: '/api/v1/device/12/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'OFF', name: 'Stove_Oven_Exhaust_1', type: 'STOVE_OVEN_EXHAUST', home: 1})
            });
        });
        $('#gwd-taparea_fridge-ON').on('click', function() {
            $.ajax({
                url: '/api/v1/device/10/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'ON', name: 'Refrigerator_1', type: 'REFRIGERATOR', home: 1})
            });
        });
        $('#gwd-taparea_fridge-OFF').on('click', function() {
            $.ajax({
                url: '/api/v1/device/10/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'OFF', name: 'Refrigerator_1', type: 'REFRIGERATOR', home: 1})
            });
        });
        $('#gwd-taparea_washer-ON').on('click', function() {
            $.ajax({
                url: '/api/v1/device/13/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'ON', name: 'C_Washer_1', type: 'CLOTHES_WASHER', home: 1})
            });
        });
        $('#gwd-taparea_washer-OFF').on('click', function() {
            $.ajax({
                url: '/api/v1/device/13/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'OFF', name: 'C_Washer_1', type: 'CLOTHES_WASHER', home: 1})
            });
        });
        $('#gwd-taparea_dish-ON').on('click', function() {
            $.ajax({
                url: '/api/v1/device/14/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'ON', name: 'Dish_Washer', type: 'DISH_WASHER', home: 1})
            });
        });
        $('#gwd-taparea_dish-OFF').on('click', function() {
            $.ajax({
                url: '/api/v1/device/14/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'OFF', name: 'Dish_Washer', type: 'DISH_WASHER', home: 1})
            });
        });

        // AC Labels are swapped on the UI
        $('#gwd-taparea_ac-ON').on('click', function() {
            $.ajax({
                url: '/api/v1/device/5/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'OFF', name: 'AC_1', type: 'AIR_CONDITIONER', home: 1})
            });
        });
        $('#gwd-taparea_ac-OFF').on('click', function() {
            $.ajax({
                url: '/api/v1/device/5/',
                dataType: 'json',
                contentType: 'application/json',
                type: 'PUT',
                data: JSON.stringify({status: 'ON', name: 'AC_1', type: 'AIR_CONDITIONER', home: 1})
            });
        });


        // setup listeners for tapareas
        $('#gwd-taparea_oven').on('click', function() {
            ns.getStatus(12, function(data) {
                if(data['status'] === 'OFF') {
                     $('#stove-12').text('0 W');
                } else {
                    $.get('/api/v1/rms/consumption?device_id=12&home_id=1&number_of_samples=1', function(data) {
                        stove12 = data['result'] * 120;
                        stove12 = Math.round(stove12 * 10) / 10;
                        $('#stove-12').text(stove12.toString() + ' W');
                    });
                }
            });
        });
        $('#gwd-taparea_dishwasher').on('click', function() {
            ns.getStatus(14, function(data) {
                if(data['status'] === 'OFF') {
                    $('#dish-washer-14').text('0 W');
                } else {
                    $.get('/api/v1/rms/consumption?device_id=14&home_id=1&number_of_samples=1', function(data) {
                        dishWasher14 = data['result'] * 120;
                        dishWasher14 = Math.round(dishWasher14 * 10) / 10;
                        $('#dish-washer-14').text(dishWasher14.toString() + ' W');
                    });
                }
            });
        });
        $('#gwd-taparea_fridge').on('click', function() {
            ns.getStatus(10, function(data) {
                if(data['status'] === 'OFF') {
                    $('#fridge-10').text('0 W');
                } else {
                    $.get('/api/v1/rms/consumption?device_id=10&home_id=1&number_of_samples=1', function(data) {
                        fridge10 = data['result'] * 120;
                        fridge10 = Math.round(fridge10 * 10) / 10;
                        $('#fridge-10').text(fridge10.toString() + ' W');
                    });
                }
            });
        });
        $('#gwd-taparea-laundry').on('click', function() {
            ns.getStatus(13, function(data) {
                if(data['status'] === 'OFF') {
                    $('#washer-13').text('0 W');
                } else {
                    $.get('/api/v1/rms/consumption?device_id=13&home_id=1&number_of_samples=1', function(data) {
                        washer13 = data['result'] * 120;
                        washer13 = Math.round(washer13 * 10) / 10;
                        $('#washer-13').text(washer13.toString() + ' W');
                    });
                }
            });
        });
        $('#gwd-taparea_ac').on('click', function() {
            ns.getStatus(5, function(data) {
                if(data['status'] === 'OFF') {
                    $('#ac-5').text('0 W');
                } else {
                    $.get('/api/v1/rms/consumption?device_id=5&home_id=1&number_of_samples=1', function(data) {
                        ac5 = data['result'] * 120;
                        ac5 = Math.round(ac5 * 10) / 10;
                        $('#ac-5').text(ac5.toString() + ' W');
                    });
                }
            });
        });
    };

    ns.getStatus = function(id, callback) {
        $.get('/api/v1/device/' + id.toString() + '/', function (data) {
            callback(data);
        });
    };

    ns.loadTotalConsumption = function() {
        // zero out the existing total consumption
        totalConsumptionValue = 0;

        var pwrnetApiUrl = '/api/v1/rms/consumption?number_of_samples=1&home_id=1&device_id=',
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
        var url = "https://api.openweathermap.org/data/2.5/weather?zip=94305,us&APPID=6faafe3de999509b86b118803ee2ca8f&units=imperial";
        $.get(url, function(data) {
            $('#weather-value').text(data['main']['temp']);
        });
    };

    onLoad();
}(demo3));