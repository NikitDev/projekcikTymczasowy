function autoCloseAlerts(){
    setTimeout(function(){
        $(".alert").alert("close");
    }, 5000);
}

$(document).ready(function(){
    autoCloseAlerts();
});
