// Scrap modals if they lose focus so they can be loaded with new content
$(document).on('hidden.bs.modal', function (e) {
    $(e.target).removeData('bs.modal');
});
/*
var glossaryList = [];
var glossaryLookup = {}

function getGlossaryList() {
    $.ajax({
        url: '/api/v1/glossarylist/?limit=0&format=json',
        dataType : 'json'
    }).done(function(data) {
        glossaryList=[]
        items = data['objects']
        for (var i = 0; i < items.length; i++) {
            item=items[i];
            glossaryLookup[item.id] = i;
            glossaryList.push({text:item.name,value:item.id});
        }
    })
    return glossaryList;
}*/

$(document).ajaxSend(function(event, request, settings) {
    $('#loading_indicator').show().addClass('loading').removeClass('hidden');
});

$(document).ajaxComplete(function(event, request, settings) {
    $('#loading_indicator').hide().removeClass('loading');
});