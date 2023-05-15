function autoCloseAlerts(){
    setTimeout(function(){
        $(".alert").alert("close");
    }, 6000);
}

$(document).ready(function(){
    autoCloseAlerts();
})