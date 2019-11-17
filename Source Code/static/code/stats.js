let url_r, e_performed, re_amount;

$(document).ready(function() {
  url_r = new Vue({
    el: "#url_registered",
    data: {
      url_registered: ""
    }
  });
  get_sURL_registered();

  re_amount = new Vue({
    el: "#redirections_performed",
    data: {
      redirections_performed: ""
    }
  });
  get_redirections_amount();

  e_performed = new Vue({
    el: "#errors_performed",
    data: {
      errors_performed: ""
    }
  });
  get_Errors_amount();
});

function get_sURL_registered() {
  $.ajax({
    url: "http://localhost:5000/amount/surl",
    method: "GET",
    success: (data, status) => {
      url_r.url_registered = data;
    }
  });
}

function get_redirections_amount() {
  $.ajax({
    url: "http://localhost:5000/amount/redirections",
    method: "POST",
    data: $("#time_re").val(),
    success: (data, status) => {
      re_amount.redirections_performed = data;
    }
  });
}

function get_Errors_amount() {
  $.ajax({
    url: "http://localhost:5000/amount/errors",
    method: "POST",
    data: $("#time_e").val(),
    success: (data, status) => {
      e_performed.errors_performed = data;
    }
  });
}
