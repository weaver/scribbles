(function($) {

    $(document).ready(function() {
        shadow($('#shadowed'));
    });

    // Animate the shadow by using trigonometry to project the shadow
    // from the light source (mouse) to the object (box center point).
    //
    // The z-height of the box is known.
    //
    // Assume that the distance from the light source to the box is a
    // fixed radius (calculated to be the distance from the center of
    // the viewport to a corner).
    //
    // The angle from the box to the light is:
    //
    //     d := (light-pos - box-pos)
    //     r := viewport-radius
    //     A = acos(d / r)
    //
    // The size of the shadow calculated separately for the X and Y
    // axes.  It is the length of the base of the triangle formed by
    // the ray of light moving past the edge of the box:
    //
    //     shadow := z-height / tan(A)
    //
    // The blur is modeled on a loose sense of atmospheric distortion.
    // The percentage of horizontal distance from the light to the box
    // is multiplied by a constant factor.
    //
    //     d_xy := distance from light to box in (x, y) plane
    //     factor := some constant factor (using z-height below)
    //     blur := (d_xy / r) * factor

    function shadow(box) {
        var name = box_shadow(),

            // Find the radius of the viewport.
            vr = radius($(window).width(), $(window).height()),

            // Fint the "z-height" of the box.
            bz = parseInt(box.css('z-index')),

            // Find the center point of the box.
            top = box.offset().top + Math.floor(box.height() / 2),
            left = box.offset().left + Math.floor(box.width() / 2);

        function draw(ev) {
            var sh = project(bz, left, ev.pageX, vr),
                sv = project(bz, top, ev.pageY, vr),
                sb = blur(bz, distance(left, top, ev.pageX, ev.pageY), vr);

            box.css(name, '#888 ' + sh + 'px ' + sv + 'px ' + sb + 'px');
        }

        $(document).mousemove(draw).click(draw);
    }

    function radius(a, b) {
        return 0.5 * Math.sqrt(Math.pow(a, 2) + Math.pow(a, 2));
    }

    function project(z, a, b, r) {
        return z / Math.tan(Math.acos((a - b) / r));
    }

    function blur(z, d, r) {
        return z * (d / r);
    }

    function distance(x1, y1, x2, y2) {
        return Math.sqrt(Math.pow(x1 - x2, 2) + Math.pow(y1 - y2, 2));
    }

    // Find the browser-specific box-shadow css property name.
    function box_shadow() {
        var prefix = '';

        if ($.browser.webkit || $.browser.safari) {
            prefix = '-webkit-';
        }
        else if ($.browser.mozilla) {
            prefix = '-moz-';
        }

        return prefix + 'box-shadow';
    }

})(jQuery);