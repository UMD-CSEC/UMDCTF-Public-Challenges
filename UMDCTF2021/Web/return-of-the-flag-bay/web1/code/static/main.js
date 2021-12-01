(function() {
    $("#defaultForm").on('submit', function(e){
        e.preventDefault();
        $.ajax({
          url: "http://127.0.0.1:5000/api/authenticate",
          type: "POST",
          datatype: "jsonp",
          data: { "username": $("#username").val(), "password": $("#password").val()},
          success: function(response){
              if (response === -1 || response === "-1"){
                $("#loginHTML").html("<div class = 'row'><div class = 'col-12'><h3 class = 'text-center'>Invalid Credentials</h3></div></div>");
              } else {
                var now = new Date();
                var minutes = 5;
                now.setTime(now.getTime()+(minutes*60*1000));
                document.cookie = "flag="+escape(response) + ";";
                document.cookie = "expires=" +now.toUTCString() + ";";
                printVal = []
                $("#loginHTML").html("<div class = 'row'><div class = 'col-12'><h3 class = 'text-center'>You are authenticated</h3></div></div>");
            }
          }
        })
    })

})()

