$(document).ready(function(){
    var yearStart = 1999;
    var yearEnd = new Date().getFullYear();
    var yearSelector = $("#year-selector")
    for(i = yearEnd; i > yearStart; i--){
        yearSelector.append($("<option>", {value: i, text: i}));
    }
})