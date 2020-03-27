var weather = weather || {};

$(document).ready(function(ns) {
    var onLoad = function() {
            // setup listeners
            setupListeners();
        },

        setupListeners = function() {
            $("#get-weather").on("click", function() {
                ns.queryWeatherBasedOnZip($("#get-weather-inpt").val());
            });
        };

    ns.queryWeatherBasedOnZip = function(zipCode) {
        // Query the OWM API for weather data
        var url = "https://api.openweathermap.org/data/2.5/weather?zip=" + zipCode +
            ",us&APPID=6faafe3de999509b86b118803ee2ca8f";
        $.get(url, function(data) {
            $("#weather-response").html(JSON.stringify(data, null, '\t'));
        });
    };

    onLoad();
}(weather));


// weather api call

var apiKey = "b9f22b3822b21d37718b37b4d5e92967";
var url = "https://api.forecast.io/forecast/";

navigator.geolocation.getCurrentPosition(success, error);

function success(position) {
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;

    $.getJSON(
        url + apiKey + "/" + latitude + "," + longitude + "?callback=?",
        function(data) {
            $("#temp").html(data.currently.temperature + "° F");
            $(".icons").html('<canvas id="' + data.minutely.icon + '" width="30" height="30"></canvas>');

            var icons = new Skycons();
            var list = ["clear-day", "clear-night", "partly-cloudy-day",
                "partly-cloudy-night", "cloudy", "rain", "sleet", "snow", "wind",
                "fog"
            ];
            for (i = 0; i < list.length; i++) {
                icons.set(list[i], list[i]);
                icons.play();
            }
        }
    );
}

function error() {
    temp.innerHTML = "Unable to retrieve your location";
}
