# Touch Events #

In mobile Safari, an iframe can capture touch events from the parent
window even if there's a DIV overlaying it. This example demonstrates
how to prevent this from happening by fighting iframes with iframes.

Load up `index.html` and move your finger across the screen. If the
black box moves, it's a success.

The "main" page is `index.html`. It loads the overlay (`draw.html`) in
an iframe by default. When the page loads, it adds the content behind
the overlay in another iframe (`page.html`). The `touchmove` event is
successfully captured by `draw.html`, not `page.html`.

Loading `page.html` first and adding `draw.html` on-demands doesn't
work. It seems like Safari binds touch events on a first come, first
served basis.
