$('.plus-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var eml = this.parentNode.children[2];
    console.log("pid =", id);

    $.ajax({
        type: "GET",
        url: "/pluscart/",
        data: {
            prod_id: id
        },
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(data) {
            console.log("data = ", data);
            eml.innerText = data.quantity;
            document.getElementById("amount").innerText = data.amount;
            document.getElementById("totalamount").innerText = data.totalamount;
        },
        error: function(xhr, status, error) {
            console.error("Error occurred: ", status, error);
            // Optionally, you can display a message to the user here
        }
    });
});

$('.minus-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var eml = this.parentNode.children[2];
    console.log("pid =", id);

    $.ajax({
        type: "GET",
        url: "/minuscart/",
        data: {
            prod_id: id
        },
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(data) {
            console.log("data = ", data);
            eml.innerText = data.quantity;
            document.getElementById("amount").innerText = data.amount;
            document.getElementById("totalamount").innerText = data.totalamount;
        },
        error: function(xhr, status, error) {
            console.error("Error occurred: ", status, error);
            // Optionally, you can display a message to the user here
        }
    });
});

$('.remove-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var eml = this
    console.log("pid =", id);

    $.ajax({
        type: "GET",
        url: "/removecart/",
        data: {
            prod_id: id
        },
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(data) {
            
            document.getElementById("amount").innerText = data.amount;
            document.getElementById("totalamount").innerText = data.totalamount;
            eml.parentNode.parentNode.parentNode.remove()
        },
        error: function(xhr, status, error) {
            console.error("Error occurred: ", status, error);
            // Optionally, you can display a message to the user here
        }
    });
});
