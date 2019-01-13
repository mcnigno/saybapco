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
    $("#anchorID").click(function(){
        var rowid = (this).data('id');
        console.log(rowid)
    }
    );
});