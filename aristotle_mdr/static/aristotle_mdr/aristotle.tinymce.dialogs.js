function glossary_submit_click_handler(){
    var g_id = $('#id_items').val()
    var link_text = $('#id_link').val();

    content = '<a class="aristotle_glossary" data-aristotle_glossary_id="'+g_id+'" href="/item/'+g_id+'">' + link_text + '</a>';
    // in case you are using a real popup window
    //window.opener.tinymce.activeEditor.selection.setContent(content);

    // in case you use a modal dialog
    tinymce.activeEditor.selection.setContent(content);
    tinyMCEPopup.close();
    return false;
}