$(document).ready(function() {
  //datepicker
  $('#datepicker').datepicker({
    format: 'mm/dd/yyyy'
  })

  function generateChart(data) {
    function attachDates(data, dates) {
      return _.map(data, function(datum, i){
        return [dates[i], +datum.toFixed(2)]
      });
    }

    const load = attachDates(data.load, data.dates)
    const lr = attachDates(data.lr, data.dates)
    const svr = attachDates(data.svr, data.dates)
    const ffnn = attachDates(data.ffnn, data.dates)

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
        color: Highcharts.getOptions().colors[1],
        marker: {
            fillColor: 'white',
            lineWidth: 1,
            lineColor: Highcharts.getOptions().colors[1]
        }
      }, {
        name: 'Forecast (Linear Regression)',
        data: lr || [],
        zIndex: 1,
        dashStyle: 'shortdash',
        lineColor: Highcharts.getOptions().colors[0],
        marker: {
            fillColor: 'white',
            lineWidth: 1,
            lineColor: Highcharts.getOptions().colors[0]
        }
      }, {
        name: 'Forecast (SVR)',
        data: svr || [],
        zIndex: 1,
        dashStyle: 'shortdash',
        color: Highcharts.getOptions().colors[0],
        marker: {
            fillColor: 'white',
            lineWidth: 1,
            lineColor: Highcharts.getOptions().colors[0]
        }
      }, {
        name: 'Forecast (FFNN)',
        data: ffnn || [],
        zIndex: 1,
        dashStyle: 'shortdash',
        color: Highcharts.getOptions().colors[0],
        marker: {
            fillColor: 'white',
            lineWidth: 1,
            lineColor: Highcharts.getOptions().colors[0]
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

    $('.model-view').addClass('loading-mask');

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

          $('.model-view').removeClass('loading-mask');
        },
        fail: function(resp){
          $('.model-view').removeClass('loading-mask');
        }
    });
  });
})