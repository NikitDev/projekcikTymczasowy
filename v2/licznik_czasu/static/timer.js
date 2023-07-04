$(document).ready(function() {
    var timerInterval, start_time, flag;
    var csrf = $("input[name=csrfmiddlewaretoken]").val();
    var project_id, task_id, session_id;
    if(who_is != 'CL' || is_superuser != true) {
        if (session_id != task_id) {
            flag = true;
            $("#timer_button").text("START");
            $("#timer_button").attr("disabled", true);
            $("#timer-display").text("Inny licznik już pracuje: " + session_id);
        }
        else {
            flag = true;
            $("#timer_button").text("START");
            $("#timer-display").text("00:00:00");
        }

        function timer1() {
            var now = new Date().getTime();
            var elapsed = now - start_time;
            var hours = Math.floor(elapsed / 3600000);
            var minutes = Math.floor((elapsed % 3600000) / 60000);
            var seconds = Math.floor((elapsed % 60000) / 1000);

            var timeString = hours.toString().padStart(2, '0') + ':' +
                minutes.toString().padStart(2, '0') + ':' +
                seconds.toString().padStart(2, '0');
            $("#timer-display").text(timeString);
        }

        function beforeUnloadHandler() {
            var path = window.location.pathname;
            var pathParts = path.split('/');
            var projectID = pathParts[2];
            var taskID = pathParts[4];
            $.ajax({
                url: '/project/' + projectID + '/task/' + taskID + '/save_view/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrf,
                },
                success: function(response) {
                },
                error: function(xhr, status, error) {
                }
            });
        }

        $("#timer_button").click(function() {
            if (flag) {
                // start
                var data = {
                    "action": "start",
                    "csrfmiddlewaretoken": csrf
                };
                $.post("", data, function(response) {
                    if (response.success) {
                        start_time = new Date().getTime();
                        timerInterval = setInterval(timer1, 1000);
                        setInterval(CallAutosave, 5000);
                    }
                });
                flag = false;
                $("#timer_button").text("STOP");

                var urlParts = window.location.pathname.split('/');
                project_id = urlParts[2];
                task_id = urlParts[4];
                window.addEventListener("beforeunload", beforeUnloadHandler);
            } else {
                // stop
                clearInterval(timerInterval);
                $('#timer-display').text('00:00:00');
                $("#timer_button").text("START");
                $.post('', {
                    'csrfmiddlewaretoken': csrf,
                    'action': "stop"
                });
                flag = true;

                window.removeEventListener("beforeunload", beforeUnloadHandler);
            }
        });
    }
});

function CallAutosave() {
     var csrf = $("input[name=csrfmiddlewaretoken]").val();
     var path = window.location.pathname;
     var pathParts = path.split('/');
     var projectID = pathParts[2];
     var taskID = pathParts[4];
     $.ajax({
        url: '/project/' + projectID + '/task/' + taskID + '/save_view_second/',
        method: 'POST',
        headers: {
                'X-CSRFToken': csrf,
        },
        success: function(response) {
            // Obsłuż odpowiedź od widoku Django
        },
        error: function(xhr, status, error) {
            // Obsłuż błąd żądania
        }
    });
}