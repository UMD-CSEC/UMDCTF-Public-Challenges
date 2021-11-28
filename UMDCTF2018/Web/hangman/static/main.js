
/* Submit letter */

$('#letter-form').submit(function (e) {
  var data = $("#letter-form").serialize();

  /* Empty input */
  $('#letter-form input').val('');

  $.ajax({
    type: "POST",
    url: '',
    data: data,
    success: function (data) {
      /* Refresh if finished */
      if (data.finished) {
        location.reload();
      }
      else {
        /* Update current */
        $('#current').text(data.current);

        /* Update errors */
        $('#errors').html(
          '<span class="text-danger">' + data.errors + '</span>');

        /* Update drawing */
        updateDrawing(data.errors);
      }
    }
  });
  e.preventDefault();
});

function updateDrawing(errors) {
  $('#hangman-drawing').children().slice(0, errors.length).show();
}
