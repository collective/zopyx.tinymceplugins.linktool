var editor = null;
var img_obj = null;
var map_obj = null;
//array of form elements
var props = [];

function init() {

	tinyMCEPopup.resizeToInnerSize();
	//tinyMCE.setWindowArg('mce_windowresize', true);//i guess we dont need this

	editor = tinyMCEPopup.editor;
	var _parent = editor.contentWindow.parent.location.href;
	selected_node = editor.selection.getNode();
    var content = document.getElementById('content');
    content.innerHTML = loadMetaInformation(_parent + '/../@@metaInformation');
}

function loadMetaInformation(url) {
    // load anchors from view @@getAnchors view
    var request = new XMLHttpRequest();
    request.open('get', url, false);
    request.send(null);
    if (request.status == 200)
        return request.responseText;
    else
        return 'An error occurred';
}


function cancelAction() {
	tinyMCEPopup.close();
}

function addLink(url, linktype, id) {
    var inst = tinyMCEPopup.editor;
    var elm, elementArray, i;
    
    elm = inst.selection.getNode();
    elm = inst.dom.getParent(elm, "A");

    tinyMCEPopup.execCommand("mceBeginUndoLevel");

    // Create new anchor elements
    if (elm == null) {
        inst.getDoc().execCommand("unlink", false, null);
        tinyMCEPopup.execCommand("CreateLink", false, url, {skip_undo : 1});

        elementArray = tinymce.grep(inst.dom.select("a"), function(n) {return inst.dom.getAttrib(n, 'href') == url;});
        for (i=0; i<elementArray.length; i++)
            setAllAttribs(elm = elementArray[i], linktype, id);  
    } 

    // Don't move caret if selection was image
    if (elm && (elm.childNodes.length != 1 || elm.firstChild.nodeName != 'IMG')) {
        inst.focus();
        inst.selection.select(elm);
        inst.selection.collapse(0);
        tinyMCEPopup.storeSelection();
    }

    tinyMCEPopup.execCommand("mceEndUndoLevel");
    tinyMCEPopup.close();
}

function setAllAttribs(elm, linktype, id) {
    var dom = tinyMCEPopup.editor.dom;
    dom.addClass(elm, 'reference-' + linktype);
    // does not work
//    dom.setAttrib(elm, 'destid', id);
}
