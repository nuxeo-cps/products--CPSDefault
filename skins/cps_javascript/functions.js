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


//**********************************************************************
function trim(s) {
    while (s.substring(0,1) == ' ') {
	s = s.substring(1,s.length);
    }
    while (s.substring(s.length-1,s.length) == ' ') {
	s = s.substring(0,s.length-1);
    }
    return s;
}


//**********************************************************************
function checkEmptySearch(formElem) {
    var query = trim(formElem.SearchableText.value);
    if (query != '') {
	return true;
    }
    formElem.SearchableText.value = query
    formElem.SearchableText.focus();
    return false;
}

//**********************************************************************
function setFocus() {
    field = document.getElementById('field_focus');
	if (field) {
	    field.focus();
	}
}
