
var temperature = {
    x: Object.values(device_data["timestamp"]),
    y: Object.values(device_data["temperature"]),
    type: 'scatter'
};

var humidity = {
    x: Object.values(device_data["timestamp"]),
    y: Object.values(device_data["rel_humidity"]),
    type: 'scatter'
};

var power = {
    x: Object.values(farm_data["timestamp"]),
    y: Object.values(farm_data["POWER_TEST_PEN"]),
    type: 'scatter'
};

var energy = {
    x: Object.values(farm_data["timestamp"]),
    y: Object.values(farm_data["energy"]),
    type: 'scatter'
};

var temperature_data = [temperature];
var humidity_data = [humidity];
var power_data = [power];
var energy_data = [energy];

Plotly.newPlot('temperature-plot', temperature_data, {title: {text: 'temperature (F)'}});
Plotly.newPlot('humidity-plot', humidity_data, {title: {text: 'humidity (%)'}});
Plotly.newPlot('power-plot', power_data, {title: {text: 'power (kW)'}});
Plotly.newPlot('energy-plot', energy_data, {title: {text: 'energy (kWh)'}});
