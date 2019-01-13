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

$('#dash_19').on(function(){
    console.log('iframe dash_19 ready');
    $(document.links).filter(function() {
        return this.hostname != window.location.hostname;
    }).attr('target', '_blank');
    console.log('i did something');
});
*/
$(function(){
    $('#179-cell').load(function(){
        $(this).show();
        console.log('iframe loaded successfully')
    });
        
});
