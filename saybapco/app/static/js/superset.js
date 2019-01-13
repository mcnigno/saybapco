console.log('superset js ready')
/*
$(document).ready(function(){
    $("#anchorID").click(function(){
        console.log('jojoj')
    }
    );
});

$(document).ready(function(){
    $("#anchorID").click(function(){
        var rowid = $(this).data('id');
        console.log(rowid);
    }
    );
});
*/
$(document.links).filter(function() {
    return this.hostname != window.location.hostname;
}).attr('target', '_blank');