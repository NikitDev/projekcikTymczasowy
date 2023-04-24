$(document).ready(function() {
    var timerInterval, start_time, elapsed;
    var csrf = $("input[name=csrfmiddlewaretoken]").val();


    $("#start_button").click(function() {
        var data = {
        "action": "start",
        "csrfmiddlewaretoken": csrf
        };
        $.post("", data, function(response) {

                if (response.success) {
                    start_time = new Date().getTime();
                    timerInterval = setInterval(function() {
                        var now = new Date().getTime();
                        elapsed = now - start_time;
                        var hours = Math.floor(elapsed / 3600000);
                        var minutes = Math.floor((elapsed % 3600000) / 60000);
                        var seconds = Math.floor((elapsed % 60000) / 1000);
                        var timeString = hours.toString().padStart(2, '0') + ':' +
                            minutes.toString().padStart(2, '0') + ':' +
                            seconds.toString().padStart(2, '0');
                        $("#timer-display").text(timeString);
                    }, 1000);
                }

        });
    });

    $("#stop_button").click(function() {
        clearInterval(timerInterval);
        $('#timer-display').text('00:00:00');
        $.post('', {
            'csrfmiddlewaretoken': csrf,
            'action': "stop"
        });
    });
});
