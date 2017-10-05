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
        var url = "http://api.openweathermap.org/data/2.5/weather?zip=" + zipCode +
                  ",us&APPID=6faafe3de999509b86b118803ee2ca8f";
        $.get(url, function(data) {
            $("#weather-response").html(JSON.stringify(data, null, '\t'));
        });
    };

    onLoad();
}(weather));