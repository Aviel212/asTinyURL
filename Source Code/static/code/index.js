var short_url;

$(document).ready(function() {
  short_url = new Vue({
    el: "#surl",
    data: {
      surl: ""
    }
  });
});

function getsurl() {
  $.ajax({
    url: "http://localhost:5000/gsurl/",
    method: "POST",
    data: $("#long_url").val(),
    success: (data, status) => {
      short_url.surl = data;
    }
  });
}
