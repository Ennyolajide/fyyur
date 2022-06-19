window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

$('.delete-venue').click(function(){
  $.ajax({
    type: 'DELETE',
    url: `venues/${$(this).data('id')}`,
  }).done(function(resp) {
    $('#flash-alert span').parent().hide();
    if(resp.success){
      window.location.href = '/'
    }else{
      $('#flash-alert span')
        .text('An error occurred while deleting Venue')
        .parent().show()
        .removeClass('hidden', 'alert-info')
        .addClass('alert-danger')
    }
  });
})
