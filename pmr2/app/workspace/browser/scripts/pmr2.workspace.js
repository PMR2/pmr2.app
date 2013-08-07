openhref = function(e) {
    e.preventDefault();
    window.location = $(context.active.target).attr('href');
}

opendata = function(e) {
    e.preventDefault();
    window.location = $(context.active.target).attr('data-src');
},

$(document).ready(function () {
    context.init({
        fadeSpeed: 100,
        filter: function ($obj){},
        above: 'auto',
        preventDoubleContext: true,
        compress: false
    });

    context.attach('.wsfmenu.open a', [
        {text: 'Open', action: openhref},
    ]);

    context.attach('.wsfmenu.download a', [
        {text: 'Open', action: openhref},
        {text: 'Download', action: opendata}
    ]);

});

