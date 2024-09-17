$(document).ready(function () {

    function getIdSelections() {
        return $.map($('#sources-table').bootstrapTable('getSelections'), function (row) {
            return row.snippet_source_id
        })
    }

    $('#sources-table').on('click-row.bs.table', function (e, row, element, field) {
        if (field != "url" && field != "disabled") {
            window.open("/repo_details/" + row.snippet_source_id, '_self');
        }
    })

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
                $('#sources-table').bootstrapTable('refresh')
            });
    }

function urlFormatter(value, row, index) {

    if (value == null) {
        return "-"
    }

    return `<a href=`+ value +`" target="_self">` + value + `</a>`
}

function enabledFormatter(value, row, index) {

    let checked = "checked";
    if (row.disabled == 1) {
        checked = "";
    }
    html = `
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" style="margin-left: -4px;" role="switch" id="toggle-sources" ` + checked + `>
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

