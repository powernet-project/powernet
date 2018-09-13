var demo2 = demo2 || {};

$(document).ready(function(ns) {
    var onLoad = function() {},
        deviceList = null,
        currentUserId = null;



    ns.setupListeners = function(devices, userId) {
        deviceList = devices;
        currentUserId = userId;

        $('#tapArea_Violation').on('click', this.triggerViolation);
        $('#tapArea-NoViolation').on('click', this.triggerBaseCondition);
        $('#tapArea_Coordinated').on('click', this.triggerCoordination);
        $('#tapArea_LightItOnFire').on('click', this.triggerTransformerMeltdown);
    };

    ns.triggerViolation = function() {
        console.warn('triggering violation');
        if(currentUserId === 1) {
            ns.setHouseLightingCondition('VIOLATION');
            ns.toggleApplianceState(5, 'AC_1', 'AIR_CONDITIONER', 'OFF');
            ns.toggleApplianceState(10, 'Refrigerator_1', 'REFRIGERATOR', 'OFF');
            ns.toggleApplianceState(12, 'Stove_Oven_Exhaust_1', 'STOVE_OVEN_EXHAUST', 'OFF');
            ns.toggleApplianceState(13, 'C_Washer_1', 'CLOTHES_WASHER', 'OFF');
            ns.toggleApplianceState(14, 'Dish_Washer', 'DISH_WASHER', 'OFF');
        } else {
            for(var i = 0; i < deviceList.length; i++) {
                ns.toggleApplianceState(deviceList[i].id, deviceList[i].name, deviceList[i].type, 'OFF');
            }
        }

    };

    ns.triggerBaseCondition = function() {
        if(currentUserId === 1) {
            ns.setHouseLightingCondition('BASE');
            ns.toggleApplianceState(5, 'AC_1', 'AIR_CONDITIONER', 'ON');
            ns.toggleApplianceState(10, 'Refrigerator_1', 'REFRIGERATOR', 'ON');
            ns.toggleApplianceState(12, 'Stove_Oven_Exhaust_1', 'STOVE_OVEN_EXHAUST', 'ON');
            ns.toggleApplianceState(13, 'C_Washer_1', 'CLOTHES_WASHER', 'ON');
            ns.toggleApplianceState(14, 'Dish_Washer', 'DISH_WASHER', 'ON');
            ns.toggleApplianceState(19, 'PW2', 'STORAGE', 'CHARGE');
        } else {
            for(var i = 0; i < deviceList.length; i++) {
                ns.toggleApplianceState(deviceList[i].id, deviceList[i].name, deviceList[i].type, 'ON');
            }
        }
    };

    ns.triggerCoordination = function() {
        if(currentUserId === 1) {
            ns.setHouseLightingCondition('COORDINATED');
            ns.toggleApplianceState(5, 'AC_1', 'AIR_CONDITIONER', 'ON');
            ns.toggleApplianceState(10, 'Refrigerator_1', 'REFRIGERATOR', 'ON');
            ns.toggleApplianceState(12, 'Stove_Oven_Exhaust_1', 'STOVE_OVEN_EXHAUST', 'ON');
            ns.toggleApplianceState(13, 'C_Washer_1', 'CLOTHES_WASHER', 'ON');
            ns.toggleApplianceState(14, 'Dish_Washer', 'DISH_WASHER', 'ON');
            ns.toggleApplianceState(19, 'PW2', 'STORAGE', 'DISCHARGE');
        } else {
            for(var i = 0; i < deviceList.length; i++) {
                ns.toggleApplianceState(deviceList[i].id, deviceList[i].name, deviceList[i].type, 'ON');
            }
        }
    };

    ns.triggerTransformerMeltdown = function() {
        if(currentUserId === 1) {
            ns.setHouseLightingCondition('VIOLATION');
            ns.toggleApplianceState(5, 'AC_1', 'AIR_CONDITIONER', 'OFF');
            ns.toggleApplianceState(10, 'Refrigerator_1', 'REFRIGERATOR', 'ON');
            ns.toggleApplianceState(12, 'Stove_Oven_Exhaust_1', 'STOVE_OVEN_EXHAUST', 'ON');
            ns.toggleApplianceState(13, 'C_Washer_1', 'CLOTHES_WASHER', 'OFF');
            ns.toggleApplianceState(14, 'Dish_Washer', 'DISH_WASHER', 'OFF');
        } else {
            for(var i = 0; i < deviceList.length; i++) {
                ns.toggleApplianceState(deviceList[i].id, deviceList[i].name, deviceList[i].type, 'OFF');
            }
        }
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