$(document).ready(function () {

    function getIdSelections() {
        return $.map($('#jobs-table').bootstrapTable('getSelections'), function (row) {
            return row.job_id
        })
    }

    $('#jobs-table').on('check.bs.table uncheck.bs.table ' + 'check-all.bs.table uncheck-all.bs.table', function () {
        $('#delete-jobs').prop('disabled', !$('#jobs-table').bootstrapTable('getSelections').length)
    })

    $('#delete-jobs').click(function () {
        let ids = getIdSelections()

        if (ids.length == 0) {
            return
        }

        let settings = {
            "url": "/delete_jobs",
            "method": "POST",
            "timeout": 0,
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        };

        let data = ""
        ids.forEach((id) => {

            if (data == "") {
                data = data + "job_ids=" + id
            } else {
                data = data + "&job_ids=" + id
            }
        });

        settings.data = data;

        $.ajax(settings)
            .fail(function (response) {
                alert(response.responseText);
            })
            .done(function (response) {
                alert(response);
                $('#jobs-table').bootstrapTable('refresh')
                $('#delete-jobs').prop('disabled', true)
            });
    })

});

function jobActionsFormatter(value, row, index) {

    let html = "";

    if (row.status != "Cancelling..." && row.status != "Cancelled" && row.status != "Completed") {
        html += `<button type="button" class="btn btn-danger" id="cancel-job">Cancel</button>`
    }

    html += `<a href="/job_details/` + row.job_id + `" target="_blank" + row.job_id class="btn btn-primary">Details</a>`
    return html;
}

window.jobActionsEvents = {
    'click #cancel-job': function (e, value, row, index) {

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
                $('#jobs-table').bootstrapTable('refresh')
            });
    }
}

