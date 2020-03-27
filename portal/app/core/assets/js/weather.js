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
        data = JSON.stringify(data, null, '\t');
        var url = "https://api.openweathermap.org/data/2.5/weather?zip=" + zipCode +
            ",us&APPID=6faafe3de999509b86b118803ee2ca8f";
        $.get(url, function(data) {
            $("#weather-response").html(data);
        });
    };

    onLoad();
}(weather));


// weather functionality for all pages
navigator.geolocation.getCurrentPosition(function(position) {
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;
    var urlPosition = "https://api.openweathermap.org/data/2.5/weather?lat=" +
        latitude + "&lon=" + longitude + "&APPID=6faafe3de999509b86b118803ee2ca8f";

    $.getJSON(urlPosition, function(data) {
        urlIcon = "http://openweathermap.org/img/wn/" + data.weather[0].icon + ".png";
        // kelvin to fahrenheit conversion
        temp = Math.round((data.main.temp - 273.15) * 1.8 + 32);
        $("#temp").html(temp + "° F");
        $("#icon").html("<img src=" + urlIcon +  ">");
    });
});
