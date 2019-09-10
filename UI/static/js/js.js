function search() {
    let payload = {
        content: $('#content').val(),
        title: $('#title').val(),
        author: $('#author').val(),
        from_date: $('#from_date').val(),
        to_date: $('#to_date').val(),
    }
    
    $.post('/search', payload, function(response){ 
        console.log(response);
    });
}