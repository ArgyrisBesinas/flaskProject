$(document).ready(function () {

    // const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    // const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    $("#import-url-submit").click(function () {
        let name = $("#import-url-name").val();
        let url = $("#import-url").val();
        let source = ""
        let licence = $("#import-url-licence").val();

        if (name == undefined || name == "") {
            alert("Please fill source name");
            return;
        }

        if (url == undefined || url == "") {
            alert("Please fill url");
            return;
        }

        if (licence == null || licence == "") {
            alert("Please select licence");
            return;
        }

        source = "raw";
         if (url.includes("https://github.com/") && url.includes("/blob/")) {
                source = "github"
         }

        // if ($("#github-url-check").length > 0 && $("#github-url-check")[0].checked) {
        //     source = "github"
        //     if (!url.includes("https://github.com/") || !url.includes("/blob/")) {
        //         alert("Invalid GitHub url");
        //         return;
        //     }
        // } else if ($("#github-url-check").length > 0 && !$("#github-url-check")[0].checked) {
        //     source = "raw";
        // } else {
        //     return;
        // }

        let settings = {
            "url": "/import_snippets_url",
            "method": "POST",
            "timeout": 0,
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "data": {
                "name": name,
                "url": url,
                "source": source,
                "licence": licence
            }
        };

        $.ajax(settings)
            .fail(function (response) {
                alert(response.responseText);
            })
            .done(function (response) {
                alert(response);
            });


    });

    $("#import-file-submit").click(function () {
        let name = $("#import-file-name").val();
        let licence = $("#import-file-licence").val();

        if (name == undefined || name == "") {
            alert("Please fill source name");
            return;
        }

        if (licence == null || licence == "") {
            alert("Please select licence");
            return;
        }

        let file = document.getElementById("import-file").files[0];
        if (file) {
            let reader = new FileReader();
            reader.readAsText(file, "UTF-8");
            reader.onload = function (evt) {
                submitJupyterText(name, evt.target.result, licence);
            }
            reader.onerror = function (evt) {
                alert("Error reading file");
            }
        } else {
            alert("Please select file")
        }

    });

    $("#import-text-submit").click(function () {
        let name = $("#import-text-name").val();
        let licence = $("#import-text-licence").val();
        let text = $("#import-text").val();

        if (name == undefined || name == "") {
            alert("Please fill source name");
            return;
        }

        if (licence == null || licence == "") {
            alert("Please select licence");
            return;
        }

        if (text == undefined || text == "") {
            alert("Please enter jupyter json");
            return;
        }

        submitJupyterText(name, text, licence);
    });

    function submitJupyterText(name, text, licence) {

        try {
            JSON.parse(text);
        } catch (e) {
            alert("Invalid Json")
            return;
        }

        let settings = {
            "url": "/import_snippets_text?name=" + name + "&licence=" + licence,
            "method": "POST",
            "timeout": 0,
            "headers": {
                "Content-Type": "application/json"
            },
            "data": text
        };

        $.ajax(settings)
            .fail(function (response) {
                alert(response.responseText);
            })
            .done(function (response) {
                alert(response);
            });
    }
});

