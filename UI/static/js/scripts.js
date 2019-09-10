// Empty JS for your own code to be here
/*function queryParams(params) {
    params.content = $('#content').val();
    params.title = $('#title').val();
    params.author = $('#author').val();
    params.from_date = $('#from_date').val();
    params.to_date = $('#to_date').val();
    
    return params;
}*/

var $table = $('#table')
var $search = $('#search')

$(function() {
    $search.click(function () {
        $table.bootstrapTable('refresh')
    });
    $('#from_date').datepicker();
    $('#to_date').datepicker();
})

function queryParams() {
    var params = {}
    $('#toolbar').find('input[name]').each(function () {
        params[$(this).attr('name')] = $(this).val();
        if(($(this).attr('name') == 'from_date') || ($(this).attr('name') == 'to_date')) {
            if ($(this).val() != '') {
                let parts = $(this).val().split('/');
                let formatted_date = parts[2] + "-" + parts[0] + "-" + parts[1] + "T00:00:00Z"
                params[$(this).attr('name')] = formatted_date;
            }
        }
            
    })
    return params;
}

function responseHandler(res) {
    return res.rows
}

function LinkFormatter(value, row, index) {
  return "<a href='"+row.url+"'>Link</a>";
}

window.ajaxOptions = {
    beforeSend: function (xhr) {
      //xhr.setRequestHeader('Custom-Auth-Token', 'custom-auth-token')
    }
}