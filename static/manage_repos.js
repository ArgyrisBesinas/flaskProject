$(document).ready(function () {

    function getIdSelections() {
        return $.map($('#sources-table').bootstrapTable('getSelections'), function (row) {
            return row.snippet_source_id
        })
    }

    $('#sources-table').on('check.bs.table uncheck.bs.table ' + 'check-all.bs.table uncheck-all.bs.table', function () {
        $('#enable-sources').prop('disabled', !$('#sources-table').bootstrapTable('getSelections').length)
        $('#disable-sources').prop('disabled', !$('#sources-table').bootstrapTable('getSelections').length)
        $('#delete-sources').prop('disabled', !$('#sources-table').bootstrapTable('getSelections').length)
    })

    $('#delete-sources').click(function () {
        let ids = getIdSelections()

        if (ids.length == 0) {
            return
        }

        let settings = {
            "url": "/delete_snippet_sources",
            "method": "POST",
            "timeout": 0,
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        };

        let data = ""
        ids.forEach((id) => {

            if (data == "") {
                data = data + "snippet_source_ids=" + id
            } else {
                data = data + "&snippet_source_ids=" + id
            }
        });

        settings.data = data;

        $.ajax(settings)
            .fail(function (response) {
                alert(response.responseText);
            })
            .done(function (response) {
                alert(response);
                $('#sources-table').bootstrapTable('refresh')
                $('#enable-sources').prop('disabled', true)
                $('#disable-sources').prop('disabled', true)
                $('#delete-sources').prop('disabled', true)
            });
    })

    $('#disable-sources').click(function () {
        toggleSources(1);
    })

    $('#enable-sources').click(function () {
        toggleSources(0);
    })

    function toggleSources(setValue) {

        let ids = getIdSelections();

        if (ids.length == 0) {
            return
        }

        let settings = {
            "url": "/toggle_snippet_sources",
            "method": "POST",
            "timeout": 0,
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data: "set_value=" + setValue
        };

        ids.forEach((id) => {
            settings.data = settings.data + "&snippet_source_ids=" + id
        });

        $.ajax(settings)
            .fail(function (response) {
                alert(response.responseText);
            })
            .done(function (response) {
                alert(response);
                $('#sources-table').bootstrapTable('refresh')
                $('#enable-sources').prop('disabled', true)
                $('#disable-sources').prop('disabled', true)
                $('#delete-sources').prop('disabled', true)
            });
    }


});


// add snippets table to details panel of source rows table
function sourceDetailFormatter(index, row) {

    let settings = {
        "url": "/get_snippets_from_source?snippet_source_id=" + row.snippet_source_id,
        "method": "GET",
        "timeout": 0,
    };

    $.ajax(settings)
        .fail(function (response) {
            $("#snippets-table-" + row.snippet_source_id).bootstrapTable()
            $("#snippets-table-no-data-" + row.snippet_source_id).html("Error loading snippets")
        })
        .done(function (response) {
            $("#snippets-table-" + row.snippet_source_id).bootstrapTable({data: JSON.parse(response)})
        });

    let html = `
        <table
          id="snippets-table-${row.snippet_source_id}"
          data-toggle="table"
          data-search="true"
          >
          <thead>
            <tr>
              <th data-field="snippet_source_id" data-visible="false">source ID</th>
              <th data-field="snippet_local_id">ID</th>
              <th data-field="description">Description</th>
              <th data-field="code" data-formatter="codeFormatter">Code</th>
              <th data-field="disabled">Disabled</th>
              <th data-formatter="toggleSnippetsFormatter" data-events="toggleSnippetsEvents" data-align="center">Toggle snippet</th>
            </tr>
            <tr class="no-data">
                <td colspan="4" id="snippets-table-no-data-${row.snippet_source_id}">>No data available in table</td>
            </tr>
          </thead>
        </table>`;

    return html;
}

function codeFormatter(value, row, index) {

    return `<pre><code>` + value + `</code></pre>`

}

function toggleSnippetsFormatter(value, row, index) {
    return `<button type="button" class="btn btn-primary " id="toggle-snippets">Toggle</button>`
}

window.toggleSnippetsEvents = {
    'click #toggle-snippets': function (e, value, row, index) {

        let snippetSourceId = row.snippet_source_id;
        let snippetLocalIds = [row.snippet_local_id];

        let disabled_now = row.disabled;
        let setValue = '9'
        if (disabled_now == 0) {
            setValue = '1'
        } else if (disabled_now == 1) {
            setValue = 0
        }

        toggleSnippetsRequest(snippetSourceId, snippetLocalIds, setValue)
    }
}

function toggleSnippetsRequest(snippetSourceId, snippetLocalIds, setValue) {

    if (snippetSourceId == null || snippetSourceId == "" || snippetLocalIds.length == 0) {
        return;
    }

    if (setValue != '0' && setValue != '1') {
        return;
    }

    let settings = {
        "url": "/toggle_snippets",
        "method": "POST",
        "timeout": 0,
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data: "snippet_source_id=" + snippetSourceId + "&set_value=" + setValue
    };

    snippetLocalIds.forEach((id) => {
        settings.data = settings.data + "&snippet_local_ids=" + id
    });

    $.ajax(settings)
        .fail(function (response) {
            alert(response.responseText);
        })
        .done(function (response) {
            // alert(response);
            let settings = {
                "url": "/get_snippets_from_source?snippet_source_id=" + snippetSourceId,
                "method": "GET",
                "timeout": 0,
            };

            $.ajax(settings)
                .done(function (response) {
                    $("#snippets-table-" + snippetSourceId).bootstrapTable('load', JSON.parse(response))
                });
        });
}