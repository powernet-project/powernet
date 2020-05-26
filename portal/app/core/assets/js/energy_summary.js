
var temperature = {
    x: Object.values(device_data["timestamp"]),
    y: Object.values(device_data["temperature"]),
    type: 'scatter'
};

var humidity = {
    x: Object.values(device_data["timestamp"]),
    y: Object.values(device_data["rel_humidity"]),
    type: 'scatter'
}

var temperature_data = [temperature];
var humidity_data = [humidity]

Plotly.newPlot('temperature-plot', temperature_data, {title: {text: 'temperature'}});
Plotly.newPlot('humidity-plot', humidity_data, {title: {text: 'humidity'}});
