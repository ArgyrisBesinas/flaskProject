$(document).ready(function () {

    $("#search-button").click(function () {
        let description_search_text = $("#search-description").val();
        let code_search_text = $("#search-code").val();
        let disabled = $("#disabled-check").prop('checked');

        let settings = {
            "url": "/search_snippets",
            "method": "POST",
            "timeout": 0,
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "data": {}
        };

        if (description_search_text != null && description_search_text !== "") {
            settings.data.description_search_text = description_search_text;
        }

        if (code_search_text != null && code_search_text !== "") {
            settings.data.code_search_text = code_search_text;
        }

        if (disabled) {
            settings.data.disabled = 1;
        }

        $.ajax(settings)
            .fail(function (response) {
                alert(response.responseText);
            })
            .done(function (response) {
                // console.log(response);
                $('#snippets-table').bootstrapTable('load', JSON.parse(response));
            });
    });

});

function codeFormatter(value, row, index) {

    return `<pre><code>` + value + `</code></pre>`
}

function toggleSnippetsFormatter(value, row, index) {
    let checked = "checked";
    if (row.snippet_disabled == 1) {
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

        let disabled_now = row.snippet_disabled;
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
                    field: 'snippet_disabled',
                    value: setValue
                })
            });
    }
}
