$(document).ready(function() {
  //datepicker
  $('#datepicker').datepicker({
    format: 'mm/dd/yyyy'
  })

  function generateChart(data) {
    const load = _.map(data.load, function(datum, i){
      return [data.dates[i], +datum.toFixed(2)]
    });

    const lr = _.map(data.lr, function(datum, i){
      return [data.dates[i], +datum.toFixed(2)]
    });

    const svr = _.map(data.svr, function(datum, i){
      return [data.dates[i], +datum.toFixed(2)]
    });

    const ffnn = _.map(data.ffnn, function(datum, i){
      return [data.dates[i], +datum.toFixed(2)]
    });

    $('.chart').highcharts({
      chart: {
        type: 'line'
      },
      title: {
        text: null
      },
      tooltip: {
        crosshairs: true,
        shared: true
      },
      xAxis: {
        type: 'datetime'
      },
      yAxis: {
        title: {
          text: 'Load (kWh)'
        }
      },
      series: [{
        name: 'Actual',
        data: load || [],
        zIndex: 1,
        marker: {
            fillColor: 'white',
            lineWidth: 2,
            lineColor: Highcharts.getOptions().colors[0]
        }
      }, {
        name: 'Forecast (Linear Regression)',
        data: lr || [],
        zIndex: 1,
        marker: {
            fillColor: 'white',
            lineWidth: 2,
            lineColor: Highcharts.getOptions().colors[1]
        }
      }, {
        name: 'Forecast (SVR)',
        data: svr || [],
        zIndex: 1,
        marker: {
            fillColor: 'white',
            lineWidth: 2,
            lineColor: Highcharts.getOptions().colors[2]
        }
      }, {
        name: 'Forecast (FFNN)',
        data: ffnn || [],
        zIndex: 1,
        marker: {
            fillColor: 'white',
            lineWidth: 2,
            lineColor: Highcharts.getOptions().colors[3]
        }
      }],
      credits: {
        enabled: false
      }
    })
  }

  $('.sp-list-item').click(function(e) {
    const spId = $(e.currentTarget).data('id');

    $('.sp-id').text(spId)

    $.ajax({
        url: `/viz/${spId}`,
        type: "GET",
        cache: true,
        dataType: "json",
        success: function(resp){
          const content = resp.content;
          const forecastDate = new Date(content.forecast_date * 1000);

          $('#datepicker').datepicker('setDate', forecastDate);
          generateChart(content.chart.data);

          $('.temperature').text(content.weather.temperature);
          $('.humidity').text(content.weather.humidity);
          $('.nmrsd-lr').text(content.nrsmd.lr.toFixed(2));
          $('.nmrsd-svr').text(content.nrsmd.svr.toFixed(2));
          $('.nmrsd-ffnn').text(content.nrsmd.ffnn.toFixed(2));
        }
    });
  });
})