$(document).ready(function(){
    // year selector
    var yearStart = 1999;
    var yearEnd = new Date().getFullYear();
    var yearSelector = $("#year-selector");
    for(var i = yearEnd; i > yearStart; i--){
        if(i == year){
            yearSelector.append($("<option>", {value: i, text: i, selected: true}));
        }else{
            yearSelector.append($("<option>", {value: i, text: i}));
        }
    }
    // month selector
    var monthSelector = $("#month-selector");
    var months = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
    for(var i = 0; i < months.length; i++){
        if(i+1 == month){
            monthSelector.append($("<option>", {value: i+1, text: months[i], selected: true}));
        }else{
            monthSelector.append($("<option>", {value: i+1, text: months[i]}));
        }
    }
})