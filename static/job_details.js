$(document).ready(function () {

    reloadJobDetails();

    let reloadId = setInterval(function () {
        let details = $("#job-details-table").bootstrapTable('getData');

        if (details[0].status == "Cancelling..." || details[0].status == "Cancelled" || details[0].status == "Completed") {
            clearInterval(reloadId);
            return;
        }

        reloadJobDetails();
    }, 5000);


});

function reloadJobDetails() {
    let job_id = $("#job-details-table").attr("custom-job-id")

    let settings = {
        "url": "/get_job_details?job_id=" + job_id,
        "method": "GET",
        "timeout": 0,
    };

    $.ajax(settings)
        .fail(function (response) {
            alert(response.responseText);
        })
        .done(function (response) {
            let job_details_json = JSON.parse(response);
            $("#job-details-table").bootstrapTable('load', [job_details_json]);

            let subtable_1 = "<table class='table table-striped'><tr><th>#</th></tr>";
            let subtable_2 = "<table class='table table-striped'><tr><th>Code</th></tr>";
            let subtable_3 = "<table class='table table-striped'><tr><th>Code snippet</th></tr>";

            let row_nr = job_details_json.job_outputs.length;
            let full_code_text = "";

            job_details_json.job_outputs.forEach(function (item, index) {
                subtable_1 += "<tr id='index_row_" + index + "'><td>" + (index + 1) + "</td></tr>";

                subtable_2 += "<tr class='custom_code_row' id='code_row_" + index + "'><td><pre><code>" + item.code + "</code></pre></td></tr>";

                subtable_3 += "<tr id='snippet_row_" + index + "'><td>" + item.snippet_source_id + ", " + item.snippet_local_id + "</td></tr>";

                full_code_text += item.code + "\n";
            })

            subtable_1 += "</table>";
            subtable_2 += "</table>";
            subtable_3 += "</table>";

            let job_output_table = "<tr><td>" + subtable_1 + "</td><td>" + subtable_2 + "</td><td>" + subtable_3 + "</td></tr>";

            $("#job-output-table").html(job_output_table);

            for (let i = 0; i < row_nr; i++) {
                let row_height = $("#code_row_" + i).height();

                $("#index_row_" + i).height(row_height);
                $("#snippet_row_" + i).height(row_height);
            }

            $('#copy-code').click(function () {
                navigator.clipboard.writeText(full_code_text);
            })

        });


}