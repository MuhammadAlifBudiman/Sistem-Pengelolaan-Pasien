$(document).ready(function () {
  if (typeof globalMessage !== "undefined") {
    showToast(globalMessage, "success", 3000);
  }
  $("#loginForm").on("submit", function (e) {
    e.preventDefault();
    sign_in();
  });
});

function sign_in() {
  const username = $("#username").val();
  const password = $("#password").val();


  $.ajax({
    type: "POST",
    url: "/api/login",
    data: {
      username,
      password,
    },
    success: function (response) {
      if (response.success) {
        window.location.replace(`/?msg=${response.message}`);
      } else {
        showToast(response.message, "error", 3000);
      }
    },
  });
}
