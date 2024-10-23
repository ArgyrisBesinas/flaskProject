$(document).ready(function () {
    reloadJobDetails();

    let reloadId = setInterval(function () {
        let details = $("#job-details-table").bootstrapTable('getData');

        if (details.length > 0 && (details[0].status == "Cancelled" || details[0].status == "Completed")) {
            clearInterval(reloadId);
            return;
        }

        reloadJobDetails();
    }, 5000);
});

function reloadJobDetails() {
    let job_id = $("#job-details-table").attr("custom-job-id");

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
            document.getElementById("view_status").textContent = job_details_json.info;
            document.getElementById("view_synth_source").textContent = job_details_json.synth_source;
            document.getElementById("cancel-job").hidden = job_details_json.status !== "Running";
            document.getElementById("progress_banner").hidden = job_details_json.status === "Completed";

            if (job_details_json.progress_percent == null) {
                $("#job-details-table").bootstrapTable('hideColumn', 'progress_percent');
            }

            $("#job-details-table").bootstrapTable('load', [job_details_json]);

            // Clear previous outputs
            $("#job-output-section").empty();

            let full_code_text = "";
            var count = 0;
            job_details_json.job_outputs.forEach(function (item, index) {
                full_code_text += item.code + "\n";
                item.code.split("\n").forEach(function (it, index) {
                    count = count + 1;
                    let codeOutput = `
                        <div class="code-output">
                            <span><a class="code-icon" href="/repo_details/${item.snippet_source_id}">${count}</a></span>
                            <span class="code-container"><code class="language-python">${(it)}</code></span>
                        </div>
                    `;

                    $("#job-output-section").append(codeOutput);
                });
            });

            // Re-initialize syntax highlighting if needed
            if (typeof Prism !== 'undefined') {
                Prism.highlightAll();
            } else if (typeof hljs !== 'undefined') {
                $('pre code').each(function (i, block) {
                    hljs.highlightBlock(block);
                });
            }

            $('#copy-code').off('click').on('click', function () {
                navigator.clipboard.writeText(full_code_text);
            });
        });
}

function escapeHtml(text) {
    return text.replace(/[&<>"'`=\/]/g, function (s) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
            '/': '&#x2F;',
            '=': '&#x3D;',
            '`': '&#x60;',
        }[s] || s;
    });

}

function statusFormatter(value, row, index) {
    if (value === "Fitting" || value === "Running") {
        return `<button type="button" class="btn btn-danger" id="cancel_job">Cancel</button>`;
    }
    return value;
}

window.statusEvents = {
    'click #cancel-job': function (e, value, row, index) {
        $('#cancel-job').prop("disabled", true);
        let job_id = row.job_id;

        if (!job_id) return;

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
            .done(function () {
                reloadJobDetails();
            });
    }
}

function progressFormatter(value, row, index) {
    return `<div class="progress" role="progressbar" aria-valuenow="${value}" aria-valuemin="0" aria-valuemax="100">
                <div class="progress-bar" style="width: ${value}%"></div>
            </div>`;
}
