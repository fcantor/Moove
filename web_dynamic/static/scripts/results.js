$(document).ready(function () {
    $('#searchButton').click(function () {
        // get value from textbox in index.html
        let origin = $('#originplace').val()
        let destination = $('#destination').val()
        let selectedDate = $('#startdate').val()
        console.log(origin)
        $.ajax({
            type: 'POST',
            url: 'http://0.0.0.0:5000/flightResults',
            contentType: 'application/json',
            data: JSON.stringify({"origin": origin, "destination": destination, "date": selectedDate}),
            dataType: 'json',
            success: function (data) {
                console.log(data);
            }
        });    
    });
});