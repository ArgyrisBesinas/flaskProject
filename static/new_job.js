$(document).ready(function () {

    $('#synthesis-text-submit').click(function () {
        let text = $("#synthesis-text").val();

        if (text == undefined || text == "") {
            alert("Please enter synthesis text json");
            return;
        }

        let settings = {
            "url": "/create_new_job",
            "method": "POST",
            "timeout": 0,
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "data": {
                "synth_source": text
            }
        };

        $.ajax(settings)
            .fail(function (response) {
                alert(response.responseText);
            })
            .done(function (response) {
                window.location.href = "/job_details/" + response;
            });
    })

});