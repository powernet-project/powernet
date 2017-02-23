$(document).ready(function() {
  //datepicker
  $('#datepicker').datepicker({
    format: 'mm/dd/yyyy'
  })

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
          const startDate = new Date(content.start_date * 1000);
          const endDate = new Date(content.end_date * 1000)

          $('#datepicker').datepicker('setStartDate', startDate);
          $('#datepicker').datepicker('setEndDate', endDate);
        }
    });
  });

  //chart
  const chart = $('.chart').highcharts({
    chart: {
      type: 'line'
    },
    title: {
      text: null
    },
    credits: {
      enabled: false
    }
  })
})