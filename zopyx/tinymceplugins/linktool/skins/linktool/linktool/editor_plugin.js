

(function() {
	tinymce.PluginManager.requireLangPack('linktool');
	
	tinymce.create('tinymce.plugins.linktoolPlugin', {
		init : function(ed, url) {
			// Register commands
			ed.addCommand('mcelinktoolPopup', function() {
				var e = ed.selection.getNode();

				// Internal image object like a flash placeholder
				if (ed.dom.getAttrib(e, 'class').indexOf('mceItem') != -1)
					return;

				ed.windowManager.open({
					file : url + '/popup.html',
					width : 800,
					height : 650,
					inline : 1
				}, {
					plugin_url : url
				});
			});

			// Register buttons
			//tinyMCE.getButtonHTML(cn, 'lang_linktool_desc', '{$pluginurl}/images/tinymce_button.gif', 'mcelinktoolPopup');
			ed.addButton('linktool', {
				title : 'LinkTool',
				cmd : 'mcelinktoolPopup',
				image : url + '/images/tinymce_button.gif'
			});
		
        ed.onNodeChange.add(function(ed, cm, n, co) {
        cm.setDisabled('linktool', co && n.nodeName != 'A');
        cm.setActive('linktool', n.nodeName == 'A' && !n.name);
        });

		},

		getInfo : function() {
			return {
				longname  : 'Image Map Editor',
				author    : 'Adam Maschek, John Ericksen',
				authorurl : 'http://linktool.googlecode.com',
				infourl   : 'http://linktool.googlecode.com',
				version   : "2.0"
			};
		}
	});

	// Register plugin
	tinymce.PluginManager.add('linktool', tinymce.plugins.linktoolPlugin);
})();


var TinyMCE_linktoolPlugin = {
	


	execCommand : function(editor_id, element, command, user_interface, value) {
		switch (command) {
			case "mcelinktoolPopup":
				var template = new Array();
				template['file']   = '../../plugins/linktool/popup.html';
				template['width']  = 700;
				template['height'] = 670;

				var inst = tinyMCE.getInstanceById(editor_id);
				var elm  = inst.getFocusElement();

				if (elm != null && tinyMCE.getAttrib(elm, 'class').indexOf('mceItem') != -1)
					return true;

				tinyMCE.openWindow(template, {editor_id : editor_id, scrollbars : "yes", resizable: "yes"});
				return true;
		}
		return false;
	},

	handleNodeChange : function(editor_id, node, undo_index, undo_levels, visual_aid, any_selection) {

		if (node == null)
			return;
			
		//check parents
		//if image parent already has imagemap, toggle selected state, if simple image, use normal state
		do {
			//console.log(node.nodeName);
			if (node.nodeName == "IMG" && tinyMCE.getAttrib(node, 'class').indexOf('mceItem') == -1) {
				if (tinyMCE.getAttrib(node, 'usemap') != '') {
					tinyMCE.switchClass(editor_id + '_linktool', 'mceButtonSelected');
				}
				else {
					tinyMCE.switchClass(editor_id + '_linktool', 'mceButtonNormal');
				}
				return true;
			}
		}
		while ((node = node.parentNode));

		//button disabled by default
		tinyMCE.switchClass(editor_id + '_linktool', 'mceButtonDisabled');
		return true;
	}

};

//tinyMCE.addPlugin("linktool", TinyMCE_linktoolPlugin);
//tinymce.PluginManager.add("linktool", tinymce.plugins.linktoolPlugin);
