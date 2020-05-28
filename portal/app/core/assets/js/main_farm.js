
// function runs when buttons on main_farm are clicked, changes button color
function switchColor(divId) {
    if ($(divId).hasClass('led-green')) {
        $(divId).addClass('led-red').removeClass('led-green');
    }
    else if ($(divId).hasClass('led-red')) {
        $(divId).addClass('led-green').removeClass('led-red');
    }
}
