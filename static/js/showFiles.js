//<script src="../static/js/showFiles.js"></script>

//////////////////

$( document ).ready(function() {
    $("#add-sku").on('click', function(e){
        isValid = checkValidState();
        if (!isValid){
            e.preventDefault();
        }
    })
    
    $("#sku").change(function(){
        $(this).removeClass("invalid");
    });

    $("#value").change(function(){
        $(this).removeClass("invalid");
    });

    $("#amount").change(function(){
        $(this).removeClass("invalid");
    });
});

var checkValidState = function(){
    var listType = $('[name="list_type"]:checked')
    var plId = $('#add-packing-select').val();
    var saleId = $('#add-sales-select').val();
    var listSelected = islistSelected(plId, saleId);

    if (!(listType.val() && listSelected)){
        $("#select-buttons").addClass("invalid");
    }

    var sku = $('#sku');
    if(!sku.val()){
        sku.addClass("invalid");
    }

    var value = $('#value');
    if(!value.val() || !$.isNumeric(value.val())){
        value.addClass("invalid");
    }

    var amount = $('#amount');
    if(!amount.val() || !$.isNumeric(amount.val())){
        amount.addClass("invalid");
    }

    if ($("#select-buttons").hasClass('invalid') || 
        sku.hasClass('invalid') || 
        value.hasClass('invalid') || 
        amount.hasClass('invalid') )
        {
            $("#invalid-message").show();
            console.log("invalid");
            return false;
        }
    else
        {
            $("#invalid-message").hide();
            console.log("valid");
            return true;
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




















