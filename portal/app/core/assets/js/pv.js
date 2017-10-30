var pv = pv || {};

$(document).ready(function(ns) {
    var onLoad = function() {
        // setup listeners
        loadPvStatus();
        loadStorageStatus();
    },

    loadPvStatus = function() {
        var enphaseUrl = 'https://api.enphaseenergy.com/api/v2/systems/1308698/summary',
            queryParams = '?datetime_format=iso8601',
            apiKeyPanelOne = '&user_id=4f546b334d6a63770a&key=4231da82ac549ee9c197071dcbc857ae';

        $.get(enphaseUrl + queryParams + apiKeyPanelOne, function(data) {
            $('#pv-status-home-one').html(JSON.stringify(data, null, '\t'));
        });
    },

    loadStorageStatus = function() {
        var storageUrl = 'https://monitoringapi.solaredge.com/sites/list',
            queryParams = '?size=5&searchText=Lyon&sortProperty=name&sortOrder=ASC',
            apiKeyStorageOne = '&api_key=UZCVK3JK5KNY1LXY8F2ZCTEWUK7X4CN5';

        $.ajax({
            url: storageUrl + queryParams + apiKeyStorageOne,
            type: 'GET',
            crossDomain: true,
            dataType: 'jsonp',
            success: function(data) {
                $('#storage-status-home-one').html(JSON.stringify(data, null, '\t'));
            },
            error: function() { alert('Failed!'); }
        });

        $.get(storageUrl + queryParams + apiKeyStorageOne, function(data) {

        });
    };

    onLoad();
}(pv));