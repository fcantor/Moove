$(document).ready(function () {
    $('#searchButton').click(function () {
        // get value from textbox in index.html
        let origin = $('#originplace').val()
        let destination = $('#destination').val()
        let selectedDate = $('#startdate').val()
        let html = '<head>' +
                        '<meta charset="utf-8">' +
                        '<title>MOOVE</title>' +

                        '<link rel="stylesheet" href="../static/styles/loading.css">' +
                        '<link href="https://fonts.googleapis.com/css?family=Ubuntu" rel="stylesheet">' +
                    '</head>' +

                    '<body>' +
                        '<header>' +
                            '<h1>One step closer to your destination...</h1>' +
                        '</header>' +
                        '<div class="cow">' +
                            '<div class="head"></div>' +
                        '</div>' +

                        '<footer>' +
                            '<a href="https://github.com/fcantor/Moove">Created by Team Moove</a>' +
                        '</footer>' +
                    '</body>';
        $.ajax({
            type: 'POST',
            url: 'http://0.0.0.0:5001/results',
            contentType: 'application/json',
            data: JSON.stringify({
                "origin": origin,
                "destination": destination,
                "selectedDate": selectedDate
            }),
            dataType: 'json',
            complete: function (data) {
                window.location.href ='http://0.0.0.0:5001/results'
            }
        });
        $("html").empty();
        $("html").append(html);
    });
});
