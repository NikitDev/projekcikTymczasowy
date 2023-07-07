$(document).ready(function() {
    var csrf = $("input[name=csrfmiddlewaretoken]").val();
    if(who_is == 'CL' && is_superuser != true) {
        show_employees();
        clientInterval = setInterval(show_employees, 5000);
    }

    function show_employees() {
        var path = window.location.pathname;
        var pathParts = path.split('/');
        var projectID = pathParts[2];
        var taskID = pathParts[4];
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/project/' + projectID + '/task/' + taskID + '/active', true);
        xhr.onload = function() {
            if(xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                if(data.length != 0) {
                var html = '';
                for(var i = 0; i < data.length; i++) {
                    html += '<p>' + data[i].imie + ' ' + data[i].nazwisko + '</p>';
                    html += '<hr>';
                }
                $("#display").html("Zadanie aktywne\n" + html);
                }
                else {
                    $("#display").text("Zadanie nieaktywne");
                }
            }
        }
        xhr.send();
    };
});