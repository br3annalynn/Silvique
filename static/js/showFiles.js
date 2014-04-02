//<script src="../static/js/showFiles.js"></script>

//////////////////

$( document ).ready(function() {
    $("#add-sku").on('click', function(e){
        isValid = checkValidState();
        if (!isValid){
            console.log("invalid");
            $("#invalid-message").html("Form is not complete");
            e.preventDefault();
        }
    })
});

var checkValidState = function(){
    var listType = $('[name="list_type"]:checked').val();

    var plId = $('#add-packing-select').val();
    var saleId = $('#add-sales-select').val();
    listSelected = islistSelected(plId, saleId);
    if (!(listType && listSelected)){
        $("#select-buttons").addClass("invalid");
    }

    var sku = $('#sku').val();
    if (!(sku)){
        $('#sku').addClass("invalid");
    }
    var value = $('#value').val();
        if (!(value)){
        $('#value').addClass("invalid");
    }
    var amount = $('#amount').val();
        if (!(amount)){
        $('#amount').addClass("invalid");
    }

    if (!(listType && listSelected && sku && value && amount)){
        return false
    }
};

var islistSelected = function(plId, saleId){
    if (plId == 0 && saleId == 0){
        return false;
    }
    return true;
}

var showFiles = function(){
    $("#select-buttons").removeClass("invalid");

    var listType = $('[name="list_type"]:checked').val();

    if (listType == "packing_list") {
        $("#add-packing-select").removeAttr("disabled");
        $("#add-sales-select").attr("disabled", "disabled");
    }
    else if(listType == "sale") {
        $("#add-sales-select").removeAttr("disabled");
        $("#add-packing-select").attr("disabled", "disabled");
    }
    
}




















