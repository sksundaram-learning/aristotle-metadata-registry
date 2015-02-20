var my_node = ''
tinyMCE.init({
    mode: "textareas",
    theme: "advanced",
    theme_advanced_buttons1 : "bold,italic,underline,separator,undo,redo,separator,bullist,numlist,separator,mdr_glossary,link,unlink",

    plugins: "spellchecker,directionality,paste,searchreplace,inlinepopups",

    setup: function(editor) {
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
                    url: '/create/glossary_search/',
                });
            }
        });

        editor.onNodeChange.add(function(ed, cm, node) {
            //console.log(node.attr("data-aristotle_glossary_id"));
            my_node = node
            glossary_id = node.getAttribute('data-aristotle_glossary_id');
            console.log(glossary_id != null)
            //cm.setDisabled('mdr_glossary', (node.nodeName != 'A'));
            cm.setDisabled('mdr_glossary',  (node.nodeName == 'A' && glossary_id == null)); // Don't allow the glossary editor if its a link, and not a glossary link
            cm.setDisabled('link',          (node.nodeName == 'A' && glossary_id != null)); // Don't allow the link editor if its a link, and is a glossary link
            //cm.setDisabled('unlink',        (node.nodeName == 'A' && glossary_id != null)); // Don't allow the unlink editor if its a link, and is a glossary link
        });
    }
});

