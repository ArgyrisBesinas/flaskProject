$(document).ready(function () {

    $('#synthesis-text-submit').click(function () {
        let text = $("#synthesis-text").val();
        let synth_method = $("#select-synth-method").val();
        let synth_licence = $("#select-synth-licence").val();

        if (text == undefined || text == "") {
            alert("Please enter synthesis text");
            return;
        }

        if (synth_method == undefined || synth_method == "") {
            alert("Please select synthesis method");
            return;
        }

        if (synth_licence == undefined || synth_licence == "") {
            alert("Please select synthesis licence");
            return;
        }

        let settings = {
            "url": "/create_new_job?synth_method="+synth_method+"&licence="+synth_licence,
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