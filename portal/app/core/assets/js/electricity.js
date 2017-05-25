var elec = elec || {};

$(document).ready(function(ns) {
    var onLoad = function() {
        var electricityPrice = $("#electricity-price").val();
        $("#converted-electricity-price").text(JSON.stringify({"price": electricityPrice}, null, '\t'));
    };

    onLoad();
}(elec));