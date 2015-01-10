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
            $('.moveablerow', panelList).each(function(index, elem) {
                $(this).find('input[name$=-order]').val(index);
                $(this).find('input[name$=-DELETE]').attr('title',"Delete item "+index)
            });
        }
    });
});

function addCode() {
    var panelList = $('#draggableTable');
    new_form = $('#formstage tr').clone().appendTo(panelList);
    num_forms = $('#draggableTable tr').length
    $(new_form).find('td input').each(function(index, elem) {
        name=[$(this).attr('name').split('-')[0],num_forms,$(this).attr('name').split('-')[2]].join('-');
    })
    $(new_form).find('td input[name$=-order]').val(num_forms)
    $('input[name=form-TOTAL_FORMS]').val(num_forms)
    return false;
}