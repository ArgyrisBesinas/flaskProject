$(document).ready(function () {

    $('#nav_search_button').click(function () {
        // alert($('#nav_search_field').val());
        window.location.href = "/job_info/" + $('#nav_search_field').val();
    });

    $('#nav_search_field').keypress(function (event) {
        // If the user presses the "Enter" key on the keyboard

        if (event.key === "Enter") {
            console.log("aaa")
            event.preventDefault();
            // Trigger the button element with a click
            $('#nav_search_button').click();
        }
    })
});