function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("Logged out!");
  window.location.href = "/";
}
