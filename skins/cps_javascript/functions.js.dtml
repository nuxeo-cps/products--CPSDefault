//**********************************************************************
// Folder content
//**********************************************************************

isSelected = false;

function toggleSelect(toggleSelectButton, selectAllText, deselectAllText) {
    formElements = toggleSelectButton.form.elements;

    if (isSelected) {
	for (i = 0; i < formElements.length; i++) {
	    formElements[i].checked = false ;
	}
	isSelected = false;
	toggleSelectButton.value = selectAllText;
    } else {
	for (i = 0; i < formElements.length; i++) {
	    formElements[i].checked = true ;
	}
	isSelected = true;
	toggleSelectButton.value = deselectAllText;
    }
}

//**********************************************************************
// Tooltips
//**********************************************************************

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
