//************************************************************
// Nuxeo javascript functions
// $Id$

//************************************************************
// Folder content
isSelected = false;

function toggleSelect(toggleSelectButton, selectAllText, deselectAllText) {
    formElements = toggleSelectButton.form.elements;

    if (isSelected) {
	for (i = 0; i < formElements.length; i++) {
	    formElements[i].checked = false;
	}
	isSelected = false;
	toggleSelectButton.value = selectAllText;
    } else {
	for (i = 0; i < formElements.length; i++) {
	    formElements[i].checked = true;
	}
	isSelected = true;
	toggleSelectButton.value = deselectAllText;
    }
}

//************************************************************
// Tooltips
function toggleElementVisibility(id) {
    element = document.getElementById(id);
    if (element) {
	if (element.style.visibility == 'hidden') {
	    element.style.visibility = 'visible';
	} else {
	    element.style.visibility = 'hidden';
	}
    }
}

function showElement(show, id) {
    element = document.getElementById(id);
    if (element) {
	if (show) {
	    element.style.visibility = 'visible';
	} else {
	    element.style.visibility = 'hidden';
	}
    }
}

//************************************************************
function trim(s) {
    if (s) {
	return s.replace(/^\s*|\s*$/g, "");
    }
    return "";
}

//************************************************************
function checkEmptySearch(formElem) {
    var query = trim(formElem.SearchableText.value);
    if (query != '') {
	formElem.SearchableText.value = query;
	return true;
    }
    formElem.SearchableText.value = query;
    formElem.SearchableText.focus();
    return false;
}

//************************************************************
function setFocus() {
    field = document.getElementById('field_focus');
    if (field) {
	field.focus();
    }
}

function validateRequiredFields(fieldIds, fieldLabels, informationText) {
    for (i = 0; i < fieldIds.length; i++) {
	element = document.getElementById(fieldIds[i]);
	if (element && !element.value) {
	    window.alert("'" + fieldLabels[i] + "' " + informationText);
	    return false;
	}
    }
    return true;
}
