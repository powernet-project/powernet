var fanData = Object.values(farmData["frq"]);
var gridPower = Object.values(farmData["grid_power"]);
var solarPower = Object.values(farmData["pv_power"]);
var temperature = Object.values(farmData["a3"]);
var humidity = Object.values(farmData["a2"]);
var serialNumber = Object.values(farmData["serial_number"]);
var fanOrder = [697151, 766935, 697145, 766944, 697149, 766929, 697160, 697147, 697156, 766940, 697153, 697144, 697146, 766936, 697157];

var data = "";

function getKeyByValue(object, value) {
    for (var prop in object) {
        if (object.hasOwnProperty(prop)) {
            if (object[prop] === value) {
                return prop;
            }
        }
    }
}

for (var i = 0; i < 15; i++) {
    data += "<tr><th>";
    data += i + 1;
    data += "</th><th>";
    if (fanData[getKeyByValue(serialNumber, fanOrder[i])] < 10) {
        data += "Off";
    }
    else {
        data += "On";
    }
    data += "</th><th>";
    data += gridPower[getKeyByValue(serialNumber, fanOrder[i])].toFixed(1);
    data += "</th><th>";
    data += solarPower[getKeyByValue(serialNumber, fanOrder[i])].toFixed(1);
    data += "</th><th>";
    data += Math.round((temperature[getKeyByValue(serialNumber, fanOrder[i])] * 9/5) + 32);
    data += "</th><th>";
    data += Math.round(humidity[getKeyByValue(serialNumber, fanOrder[i])]);
    data += "</th></tr>";
}

$("#local-fan-data").html(data);
