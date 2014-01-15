

//////////////////

$.get('/get_lists', results);

function results(result){
    var lists = $.parseJSON(result);

    salesList = lists['sales_list'];
    inventoryList = lists['inventory_list'];
    fillInFiles(salesList, inventoryList)
    addClickEvents()

}

function fillInFiles(salesList, inventoryList){
    for(var i = 0; i < inventoryList.length; i++){
        $('#inventory').append('<p class="files" id="inv' + i + '">' + inventoryList[i] + '</p>');
    } 
    for(var i = 0; i < salesList.length; i++){
        $('#sales').append('<p class="files" id="sale' + i + '">' + salesList[i] + '</p>');
    }   
}

function addClickEvents(){
    $('.files').click(function(){
        var tableName = $(this).text();
        console.log(tableName);
    })

}















