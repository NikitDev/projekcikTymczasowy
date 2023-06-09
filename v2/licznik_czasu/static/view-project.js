$(document).on("submit", "#task-form", function(e){
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: "",
        data: {
            task_name: $("#id_task_name").val(),
            description: $("#id_description").val(),
            csrfmiddlewaretoken: csrfToken
        },
        success: function(response){
            $("#id_task_name").val("");
            $("#id_description").val("");
            $("#task-grid").load(location.href + " #task-grid>*", "");
            $("#messages").load(location.href + " #messages>*", "");
            autoCloseAlerts();
            console.log(response.message);
        },
        error: function(response){
            console.log(response.message);
        }
    });
});