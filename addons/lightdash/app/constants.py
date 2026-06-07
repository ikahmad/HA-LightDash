_SW_SCRIPT = (
    '<script>'
    'if(navigator.serviceWorker){navigator.serviceWorker.getRegistrations().then(function(r){'
    'for(var i=0;i<r.length;i++){r[i].unregister()}})}'
    '</script>\n'
)
