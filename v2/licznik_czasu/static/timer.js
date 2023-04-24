$(document).ready(function() {
    var timerInterval, start_time, flag;
    var csrf = $("input[name=csrfmiddlewaretoken]").val();


    if (!(value == 'None')) {
        start_time = new Date(parseInt(value)*1000);
        timerInterval = setInterval(timer1, 1000);
        flag = false;
    }
    else {
        flag = true;
    };

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
    };

    $("#timer_button").click(function() {
        if (flag) {
            var data = {
            "action": "start",
            "csrfmiddlewaretoken": csrf
            };
            $.post("", data, function(response) {
                    if (response.success) {
                        start_time = new Date().getTime();
                        timerInterval = setInterval(timer1, 1000);
                    }
            });
            flag = false;
        }
        else {
            clearInterval(timerInterval);
            $('#timer-display').text('00:00:00');
            $.post('', {
                'csrfmiddlewaretoken': csrf,
                'action': "stop"
            });
            flag = true;
        };
    });
});