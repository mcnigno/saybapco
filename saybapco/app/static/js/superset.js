console.log('superset js ready')
/*
$(document).ready(function(){
    $("#anchorID").click(function(){
        console.log('jojoj')
    }
    );
});
*/
$(document).ready(function(){
    $("#anchorID").data('id').click(function(){
        console.log('jojoj')
    }
    );
});