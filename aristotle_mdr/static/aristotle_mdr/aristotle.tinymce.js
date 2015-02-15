tinyMCE.init({
    mode: "textareas",
    theme: "advanced",
    theme_advanced_buttons1 : "bold,italic,underline,separator,undo,redo,separator,bullist,numlist,separator,glossary,link,unlink",

    plugins: "spellchecker,directionality,paste,searchreplace,inlinepopups",

    setup:function(editor) {
    getGlossaryList(); 

    editor.addButton('glossary', {
        title : 'Insert glossary item',
        text: 'Glossary',
        classes: 'widget btn aristotle-icon aristotle-glossary',
        onclick: function() {
            editor.windowManager.open( {
                inline: true,
                title: 'Insert glossary item',
                url: '/create/glossary_search/',
                body: [{
                    type: 'listbox',
                    name: 'term',
                    label: 'Select a term',
                    'values':getGlossaryList()
                },
                {
                    type: 'textbox',
                    name: 'text',
                    label: 'Link text (leave blank to use to the glossary name)'
                }],
                onsubmit: function( e ) {
                    alert('HELP!!');
                    i = e.data.term;
                    text = e.data.text || glossaryLookup[i].name;
                    editor.insertContent( '<a class="aristotle_glossary" data-aristotle_glossary_id="'+i+'" href="'+glossaryLookup[i].url+'">' + text + '</a>');
                }
            });
        }
    });

}
});
