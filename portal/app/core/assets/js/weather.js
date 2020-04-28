var weather = weather || {};
var owmUrl = "https://api.openweathermap.org/data/2.5/weather?"
var appid = "6faafe3de999509b86b118803ee2ca8f";

$(document).ready(function(ns) {
    var onLoad = function() {
            // setup listeners
            setupListeners();
            ns.queryWeatherBasedOnCoords();
        },

        setupListeners = function() {
            $("#get-weather").on("click", function() {
                ns.queryWeatherBasedOnZip($("#get-weather-inpt").val());
            });
        };

    ns.queryWeatherBasedOnZip = function(zipCode) {
        // Query the OWM API for weather data by zip code
        ns.owmApiCall(zipCode, null, null).then(function(data){
            $("#weather-response").html(JSON.stringify(data, null, '\t'));
        });
    };

    ns.queryWeatherBasedOnCoords = function() {
        // Query the OWM API for weather data by geolocation
        navigator.geolocation.getCurrentPosition(function(position) {
            let latitude = position.coords.latitude;
            let longitude = position.coords.longitude;
            ns.owmApiCall(null, latitude, longitude).then(function(data) {
                let urlIcon = "http://openweathermap.org/img/wn/" + data.weather[0].icon + ".png";
                let temp = Math.round(data.main.temp);
                $("#temp").html(temp + "° F");
                $("#icon").html("<img src=" + urlIcon +  ">");
            }).fail(function(){
                $("#temp").html("- -");
            });
        });
    };

    ns.owmApiCall = function(zipcode, latitude , longitude) {
        // OWM API call
        let url = owmUrl + "APPID=" + appid;
        if (zipcode) {
            url += "&zip=" + zipcode;
        } else {
            url += "&lat=" + latitude + "&lon=" + longitude + "&units=imperial";
        }
        return $.get(url);
    };

    onLoad();
}(weather));
