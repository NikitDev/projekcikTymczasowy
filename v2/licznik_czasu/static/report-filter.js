function showDiv(divId, element)
{
    document.getElementById(divId).style.display = element.value == "other" ? 'block' : 'none';
}
