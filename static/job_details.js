$(document).ready(function () {

    reloadJobDetails();

    let reloadId = setInterval(function () {
        let details = $("#job-details-table").bootstrapTable('getData');

        if (details[0].status == "Cancelled" || details[0].status == "Completed") {
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
            if (job_details_json.progress_percent == null) {
                 $("#job-details-table").bootstrapTable('hideColumn', 'progress_percent')
            }

            $("#job-details-table").bootstrapTable('load', [job_details_json]);

            // let subtable_1 = "<table class='table table-striped'><tr><th>#</th></tr>";
            let subtable_2 = "<table class='table table-striped'><tr><th>Code</th></tr>";
            let subtable_3 = "<table class='table table-striped'><tr><th style='text-align:center'>Source</th></tr>";

            let row_nr = job_details_json.job_outputs.length;
            let full_code_text = "";

            job_details_json.job_outputs.forEach(function (item, index) {
                // subtable_1 += "<tr id='index_row_" + index + "'><td>" + (index + 1) + "</td></tr>";

                subtable_2 += "<tr class='custom_code_row' id='code_row_" + index + "'><td><pre><code>" + item.code + "</code></pre></td></tr>";

                //  item.snippet_source_id + ", " + item.snippet_local_id
                subtable_3 += "<tr id='snippet_row_" + index + "'><td style='text-align:center'>" +
                    `<div class="btn btn-primary">
                        <a class="nav-link" href="/repo_details/`+ item.snippet_source_id +`" >
                            <i class="bi bi-eye"></i>
                        </a>
                    </div>` +
                "</td></tr>";

                full_code_text += item.code + "\n";
            })

            // subtable_1 += "</table>";
            subtable_2 += "</table>";
            subtable_3 += "</table>";

            // let job_output_table = "<tr><td>" + subtable_1 + "</td><td>" + subtable_2 + "</td><td>" + subtable_3 + "</td></tr>";
            let job_output_table = "<tr><td>" + subtable_2 + "</td><td>" + subtable_3 + "</td></tr>";

            $("#job-output-table").html(job_output_table);

            for (let i = 0; i < row_nr; i++) {
                let row_height_1 = $("#code_row_" + i).height();
                let row_height_2 = $("#snippet_row_" + i).height();

                if (row_height_1 > row_height_2) {
                    $("#code_row_" + i).height(row_height_1);
                    $("#snippet_row_" + i).height(row_height_1);
                }
                else {
                    $("#code_row_" + i).height(row_height_2);
                    $("#snippet_row_" + i).height(row_height_2);
                }
            }

            $('#copy-code').click(function () {
                navigator.clipboard.writeText(full_code_text);
            })

        });
}

function statusFormatter(value, row, index) {

    let html = value;

    if (value == "Fitting" || value == "Running") {
        html = `<button type="button" class="btn btn-danger" id="cancel-job">Cancel</button>`
    }

    return html;
}

window.statusEvents = {
    'click #cancel-job': function (e, value, row, index) {

        $('#cancel-job').prop( "disabled", true );;

        let job_id = row.job_id;

        if (job_id == null) {
            return;
        }

        let settings = {
            "url": "/cancel_job",
            "method": "POST",
            "timeout": 0,
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data: "job_id=" + job_id
        };

        $.ajax(settings)
            .fail(function (response) {
                alert(response.responseText);
            })
            .done(function (response) {
                // $('#job-details-table').bootstrapTable('refresh')
                reloadJobDetails();
            });
    }
}

function progressFormatter(value, row, index) {

     let html = `<div class="progress" role="progressbar" aria-valuenow="`+value+`" aria-valuemin="0" aria-valuemax="100">
                          <div class="progress-bar" style="width: `+value+`%"></div>
                        </div>`

    return html;
}