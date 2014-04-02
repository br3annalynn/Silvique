//<script src="../static/js/showFiles.js"></script>

//////////////////

var showFiles = function(){
    var list_type = $('[name="list_type"]:checked').val();

    if (list_type == "packing_list") {
        $("#add-packing-select").removeAttr("disabled");
        $("#add-sales-select").attr("disabled", "disabled");
    }
    else if(list_type == "sale") {
        $("#add-sales-select").removeAttr("disabled");
        $("#add-packing-select").attr("disabled", "disabled");
    }
    
}




















