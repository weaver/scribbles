define(function() {
  var block = $('#block');

  $('body').bind('touchmove', function(ev) {
    ev.preventDefault(); // Stop Safari from scrolling.
    var touch = ev.originalEvent.touches[0];
    block.css({ top: touch.screenY, left: touch.screenX });
  });

});