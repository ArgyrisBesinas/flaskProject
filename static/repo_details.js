$(document).ready(function () {

    $('#delete-sources').click(function () {

        let ids = [$(this).attr("custom-source-id")]

        if (!confirm('Are you sure you want to delete this source?')) {
            return;
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
                // alert(response);
                window.open("/manage_repos", '_self');
            });
    })

});

function toggleSources(ids, setValue) {

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
                $('#source-details-table').bootstrapTable('refresh')
            });
    }

function urlFormatter(value, row, index) {

    if (value == null) {
        return "-"
    }

    return `<a href=`+ value +`" target="_blank">` + value + `</a>`
}

function enabledFormatter(value, row, index) {

    let checked = "checked";
    if (row.disabled == 1) {
        checked = "";
    }
    html = `
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" role="switch" id="toggle-sources" ` + checked + `>
        </div>`

    return html
}

window.toggleEnabledEvents = {
    'click #toggle-sources': function (e, value, row, index) {

        let snippetSourceId = row.snippet_source_id;

        let disabled_now = row.disabled;
        let setValue = '9'
        if (disabled_now == 0) {
            setValue = '1'
        } else if (disabled_now == 1) {
            setValue = 0
        }

        $('#toggle-sources').prop('disabled', true)

        toggleSources([snippetSourceId], setValue);

    }
}






function codeFormatter(value, row, index) {

    return `<pre><code>` + value + `</code></pre>`
}

function toggleSnippetsFormatter(value, row, index) {
    let checked = "checked";
    if (row.disabled == 1) {
        checked = "";
    }
    html = `
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" role="switch" id="toggle-snippets" ` + checked + `>
        </div>`

    return html
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
                $('#snippets-table').bootstrapTable('updateCell', {
                    index: index,
                    field: 'disabled',
                    value: setValue
                })
            });
    }
}
