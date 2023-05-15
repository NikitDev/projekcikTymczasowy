$(document).on("submit", "#task-info-form", function(e){
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: "",
        data: {
            action: "task-info-form",
            task_name: $("#id_task_name").val(),
            description: $("#id_description").val(),
            csrfmiddlewaretoken: csrfToken
        },
        success: function(response){
            $("#messages").load(location.href + " #messages>*", "");
            autoCloseAlerts();
            console.log(response.message);
        },
        error: function(response){
            console.log(response.message);
        }
    }); 
});

$(document).on("submit", "#employee-form", function(e){
    e.preventDefault();
    var employees = $("input[name='employee']");
    var employeeSelection = [];
    for(var element of employees){
        if(element.checked){
            employeeSelection.push(element.value);
        }
    }
    $.ajax({
        type: "POST",
        url: "",
        data: {
            action: "employee-form",
            employee: employeeSelection,
            csrfmiddlewaretoken: csrfToken
        },
        success: function(response){
            $("#employee-table").load(location.href + " #employee-table>*", "");
            console.log(response.message);
        },
        error: function(response){
            console.log(response.message);
        },
        traditional: true
    }); 
});