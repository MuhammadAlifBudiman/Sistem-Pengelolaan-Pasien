$(document).ready(function () {
  $("#loginForm").on("submit", function (e) {
    e.preventDefault();
    sign_in();
  });
});

function sign_in() {
  const username = $("#username").val();
  const password = $("#password").val();

  if (!username) {
    alert("Please input your username.");
  }

  if (!password) {
    alert("Please input your password.");
  }

  $.ajax({
    type: "POST",
    url: "/api/login",
    data: {
      username,
      password,
    },
    success: function (response) {
      if (response.success) {
        alert(response["message"]);
        $.cookie("mytoken", response.data.token);
        window.location.replace("/");
      } else {
        alert(response["message"]);
      }
    },
  });
}
