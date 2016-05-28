/*$(document).bind('hilightChoice', function(e, choice, autocomplete) {
    offset = $(choice).offset().top-$(choice).parent().offset().top
    $(choice).parent().scrollTop(offset);
});
*/
$( document ).ready( function() {
    $('a.ac_preview_link').click( function(e) {
        e.stopPropagation();
        return false;
    });
});