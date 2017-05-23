var elec = elec || {};

$(document).ready(function(ns) {
    var onLoad = function() {
        // query for electricity data
        ns.queryElectricityPrice();
    };

    ns.queryElectricityPrice = function(zipCode) {
        // Query the OWM API for weather data
        var url = "https://hourlypricing.comed.com/api?type=currenthouraverage";
        $.get(url, function(data) {
            $("#electricity-response").html(JSON.stringify(data));
        });
    };

    onLoad();
}(elec));