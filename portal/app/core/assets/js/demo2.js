var demo2 = demo2 || {};

$(document).ready(function(ns) {
    var onLoad = function() {};

    ns.setupListeners = function() {
        $('#tapArea_Violation').on('click', this.triggerViolation);
        $('#tapArea-NoViolation').on('click', this.triggerBaseCondition);
        $('#tapArea_Coordinated').on('click', this.triggerCoordination);
        $('#tapArea_LightItOnFire').on('click', this.triggerTransformerMeltdown);
    };

    ns.triggerViolation = function() {
        console.warn('triggering violation');
        ns.setHouseLightingCondition('VIOLATION');
        ns.toggleApplianceState(5, 'AC_1', 'AIR_CONDITIONER', 'OFF');
        ns.toggleApplianceState(10, 'Refrigerator_1', 'REFRIGERATOR', 'OFF');
        ns.toggleApplianceState(12, 'Stove_Oven_Exhaust_1', 'STOVE_OVEN_EXHAUST', 'OFF');
        ns.toggleApplianceState(13, 'C_Washer_1', 'CLOTHES_WASHER', 'OFF');
        ns.toggleApplianceState(14, 'Dish_Washer', 'DISH_WASHER', 'OFF');
    };

    ns.triggerBaseCondition = function() {
        ns.setHouseLightingCondition('BASE');
        ns.toggleApplianceState(5, 'AC_1', 'AIR_CONDITIONER', 'ON');
        ns.toggleApplianceState(10, 'Refrigerator_1', 'REFRIGERATOR', 'ON');
        ns.toggleApplianceState(12, 'Stove_Oven_Exhaust_1', 'STOVE_OVEN_EXHAUST', 'ON');
        ns.toggleApplianceState(13, 'C_Washer_1', 'CLOTHES_WASHER', 'ON');
        ns.toggleApplianceState(14, 'Dish_Washer', 'DISH_WASHER', 'ON');
        ns.toggleApplianceState(19, 'PW2', 'STORAGE', 'CHARGE');
    };

    ns.triggerCoordination = function() {
        ns.setHouseLightingCondition('COORDINATED');
        ns.toggleApplianceState(5, 'AC_1', 'AIR_CONDITIONER', 'ON');
        ns.toggleApplianceState(10, 'Refrigerator_1', 'REFRIGERATOR', 'ON');
        ns.toggleApplianceState(12, 'Stove_Oven_Exhaust_1', 'STOVE_OVEN_EXHAUST', 'ON');
        ns.toggleApplianceState(13, 'C_Washer_1', 'CLOTHES_WASHER', 'ON');
        ns.toggleApplianceState(14, 'Dish_Washer', 'DISH_WASHER', 'ON');
        ns.toggleApplianceState(19, 'PW2', 'STORAGE', 'DISCHARGE');
    };

    ns.triggerTransformerMeltdown = function() {
        ns.setHouseLightingCondition('VIOLATION');
        ns.toggleApplianceState(5, 'AC_1', 'AIR_CONDITIONER', 'OFF');
        ns.toggleApplianceState(10, 'Refrigerator_1', 'REFRIGERATOR', 'OFF');
        ns.toggleApplianceState(12, 'Stove_Oven_Exhaust_1', 'STOVE_OVEN_EXHAUST', 'OFF');
        ns.toggleApplianceState(13, 'C_Washer_1', 'CLOTHES_WASHER', 'OFF');
        ns.toggleApplianceState(14, 'Dish_Washer', 'DISH_WASHER', 'OFF');
    };

    ns.toggleApplianceState = function(id, name, type, state) {
        $.ajax({
            url: '/api/v1/device/' + id.toString() + '/',
            dataType: 'json',
            contentType: 'application/json',
            type: 'PUT',
            data: JSON.stringify({status: state, name: name, type: type})
        });
    };

    ns.setHouseLightingCondition = function(condition) {
        $.ajax({
            url: '/api/v1/hue_states/1/',
            dataType: 'json',
            contentType: 'application/json',
            type: 'PUT',
            data: JSON.stringify({state: condition, id: 1})
        });
    };

    onLoad();
}(demo2));