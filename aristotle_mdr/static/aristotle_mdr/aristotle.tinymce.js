tinymce.PluginManager.add('aristotle_glossary', function(editor, url) {

        editor.addButton('mdr_glossary', {
            title : 'Insert glossary item',
            text: 'Glossary',
            label: 'Glossary',
            icons:false,
            'class': 'mce_anchor',
            onclick: function() {
                editor.windowManager.open( {
                    inline: true,
                    title: 'Insert glossary item',
                    url: '/dialog/glossary_search/',
                });
            }
        });

        editor.onNodeChange.add(function(ed, cm, node) {
            //console.log(node.attr("data-aristotle_glossary_id"));
            glossary_id = node.getAttribute('data-aristotle_glossary_id');
            //cm.setDisabled('mdr_glossary', (node.nodeName != 'A'));
            cm.setDisabled('mdr_glossary',  (node.nodeName == 'A' && glossary_id == null)); // Don't allow the glossary editor if its a link, and not a glossary link
            cm.setDisabled('link',          (node.nodeName == 'A' && glossary_id != null)); // Don't allow the link editor if its a link, and is a glossary link
            //cm.setDisabled('unlink',        (node.nodeName == 'A' && glossary_id != null)); // Don't allow the unlink editor if its a link, and is a glossary link
        });
    //}
});