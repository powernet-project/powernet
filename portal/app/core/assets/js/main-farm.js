var averageHum = math.mean(Object.values(tempHum["rel_humidity"]));
var averageTemp = math.mean(Object.values(tempHum["temperature"]));

$("#average-temp").html(Math.round(averageTemp) + "F");
$("#average-temp2").html(Math.round(averageTemp) + "F");

$("#average-hum").html(Math.round(averageHum) + "%");
$("#average-hum2").html(Math.round(averageHum) + "%");

$("#pen1").html(Math.round(Math.abs(penPower["POWER_TEST_PEN"])) + "W");
$("#pen2").html(Math.round(Math.abs(penPower["CONTROL_FAN_POWER"])) + "W");

var fanData = Object.values(pen1Fan["frq"]);
var controlData = Object.values(penPower["CONTROL_FAN_POWER"]);
var serialNumber = Object.values(pen1Fan["serial_number"]);
var fanOrder = [697151, 766935, 697145, 766944, 697149, 766929, 697160, 697147, 697156, 766940, 697153, 697144, 697146, 766936, 697157];


function getKeyByValue(object, value) {
    for (var prop in object) {
        if (object.hasOwnProperty(prop)) {
            if (object[prop] === value) {
                return prop;
            }
        }
    }
}

for (var x = 0; x < fanData.length; x++) {
    if (fanData[getKeyByValue(serialNumber, fanOrder[x])] < 10) {
        $("#fan" + x).addClass('led-red').removeClass('led-green');
    }
    if (Math.abs(controlData) < 2000) {
        $("#control" + x).addClass('led-red').removeClass('led-green');
    }
}

// function runs when divs on main_farm are clicked, changes button color
function switchColor(divId) {
    if ($(divId).hasClass('led-green')) {
        $(divId).addClass('led-red').removeClass('led-green');
    }
    else if ($(divId).hasClass('led-red')) {
        $(divId).addClass('led-green').removeClass('led-red');
    }
}
