$(document).on("submit", "#task-form", function(e){
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: "",
        data: {
            task_name: $("#id_task_name").val(),
            description: $("#id_description").val(),
            project_id: projectId,
            csrfmiddlewaretoken: csrfToken
        },
        success: function(response){
            $("#id_task_name").val("");
            $("#id_description").val("");
            $("#task-grid").load(location.href + " #task-grid>*", "");
            console.log(response.message);
        },
        error: function(response){
            console.log(response.message);
        }
    });
});$