
function toggleFormTooltip(id) {
    element = document.getElementById(id);
    if (element) {
	if (element.style.visibility == 'hidden') {
	    element.style.visibility = 'visible';
	} else {
	    element.style.visibility = 'hidden';
	}
    }
}

function showFormTooltip(show, id) {
    element = document.getElementById(id);
    if (element) {
	if (show) {
	    element.style.visibility = 'visible';
	} else {
	    element.style.visibility = 'hidden';
	}
    }
}
