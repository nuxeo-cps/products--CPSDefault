
//**********************************************************************
// Folder content
//**********************************************************************

isSelected = false;

function toggleSelect(toggleSelectButton) {
    formElements = toggleSelectButton.form.elements;

    if (isSelected == false) {
	for (i = 0; i < formElements.length; i++) {
	    formElements[i].checked = true ;
	}
	isSelected = true;
	//toggleSelectButton.value = "button_deselect_all";
    } else {
	for (i = 0; i < formElements.length; i++) {
	    formElements[i].checked = false ;
	}
	isSelected = false;
	//toggleSelectButton.value = "button_select_all";
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
