// Set (then unset) this to supress the ajax loading animation
var suppressLoadingBlock = false;

// Scrap modals if they lose focus so they can be loaded with new content
$(document).on('hidden.bs.modal', function (e) {
    $(e.target).removeData('bs.modal');
});

$(document).ajaxSend(function(event, request, settings) {
    if (!suppressLoadingBlock) {
        $('#loading_indicator').show().addClass('loading').removeClass('hidden');
    }
});

$(document).ajaxComplete(function(event, request, settings) {
    $('#loading_indicator').hide().removeClass('loading');
});

function itemFromId (msg,id) {
    var item = {name:'id: '+id,description:"error"}
    $.each(msg,function(i,glossary_item) {
        if (glossary_item.id == id) {
            item = glossary_item
        }
    })

    return item;
}

$(document).ready(function () {
    generateGlossaryPopovers();
});

function generateGlossaryPopovers() {
    var glossary_list = []
    $('[data-aristotle_glossary_id]').each(function(i){
        glossary_list.push($(this).data("aristotle_glossary_id"))
    })

    if (glossary_list != []) {
        suppressLoadingBlock = true;
        $.ajax({
          type: "GET",
          url: "/api/v1/glossarylist/",
          data: { id__in: glossary_list, },
          traditional : true
        })
        .done(function( msg ) {
            glossary_list = msg.objects
            suppressLoadingBlock = false;

            $('[data-aristotle_glossary_id]').each(function(i){
                item = itemFromId(glossary_list,$(this).data('aristotle_glossary_id'))
                $(this).addClass("glossary_link")
                    .attr('title',item.name)
                    .data('toggle','popover')
                    .data('trigger','hover')
                    .data('content',item.description)
                $(this).css("border-bottom","1px dashed #55f")
          });
          $('[data-aristotle_glossary_id]').popover()
        })
    }
}