jQuery(function($) {
    var panelList = $('#draggableTable');

    panelList.sortable({
        // Only make the .panel-heading child elements support dragging.
        // Omit this to make the entire <li>...</li> draggable.
        handle: '.grabber',
        start: function () {
            $(this).addClass('info');
            $('.grabber').addClass('grabbed');
        },
        stop: function () {
          $('.grabber').removeClass('grabbed');
        },

        update: function() {
            reorderRows();
        }
    });
    $( "form" ).submit(function( event ) {
        $( "table#formset #draggableTable tr" ).each(function() {
            var row = this;
            if ( $(row).find( "input[name$=-id]" ).val() == "" ) {
                var all_empty = true;
                $(row).find(':input').each(function() {
                    var name = $(this).attr('name').split('-')[2];
                    if (name !== name.toUpperCase()) {
                        // We skip all uppercase ones as they are Django sepcial fields
                        all_empty = all_empty && ( $(this).val() === "" )
                    }
                })
                if (all_empty) {
                    // We could delete it, but that might be visually disturbing
                    // Lets just forcefully null everything
                    $(row).find(':input').each(function() {
                        $(this).val(null)
                    })
                }
            }
        })
        return;
    });
});

function addCode() {
    var panelList = $('#draggableTable');
    new_form = $('#formstage tr').clone().appendTo(panelList);
    num_forms = $('#draggableTable tr').length
    $(new_form).find('input').attr('value','');
    $(new_form).find('input[name$="-id"]').removeAttr('value');
    // rename the form entries
    $('input[name=form-TOTAL_FORMS]').val(num_forms)
    return false;
}

function renumberRow(row,num) {
    $(row).find('input[name$="-ORDER"]').attr('value',num);
    // $(row).find(':input').each(function(index, elem) {
    //     name=[$(this).attr('name').split('-')[0],num,$(this).attr('name').split('-')[2]].join('-');
    //     $(this).attr('name',name);
    //     $(this).attr('id',"id_"+name);
    // });
}

function reorderRows(panelList) {
    //var panelList = $('#draggableTable');

    $('.moveablerow', panelList).each(function(index, elem) {
        renumberRow(this,index);
        $(this).find('input[name$=-DELETE]').attr('title',"Delete item "+index);
    });
}

function addSlot() {
    var panelList = $('#slotsTable');
    new_form = $('#slotsTable tr:first').clone().appendTo(panelList);
    num_forms = $('#slotsTable tr').length
    $(new_form).find('input').attr('value','');
    $(new_form).find('input[name$="-id"]').removeAttr('value');
    reorderRows(panelList);
    // rename the form entries
    $('input[name=slots-TOTAL_FORMS]').val(num_forms)
    return false;
}
