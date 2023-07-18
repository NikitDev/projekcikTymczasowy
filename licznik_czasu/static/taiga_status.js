$(document).ready(function() {
    var csrf = $("input[name=csrfmiddlewaretoken]").val();
    if (who_is == 'EM' || is_superuser == true) {
        show_taiga_status();
        clientInterval = setInterval(show_taiga_status, 5000);
    }

    function show_taiga_status() {
        fetch('/status/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrf
            }
        })
        .then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Błąd sieci');
            }
        })
        .then(function(data) {
            if (data.length != 0) {
                var status = data[0];
                var html = status ? 'Aktywna' : 'Niekatywna';
                $("#status_taiga").html("Synchronizacja Taigi: " + html);
            }
        })
        .catch(function(error) {
            console.log(error);
        });
    }
});
