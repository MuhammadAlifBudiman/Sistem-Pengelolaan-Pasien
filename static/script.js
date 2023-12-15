function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  // showToast("You have been logged out.", "success", 3000)
  // showAlert();
  // setTimeout(function () {
  //   window.location.href = "/";
  // }, 3000);
  window.location.href = `/?msg=You have been logged out.`;
}

// Display a toast notification
function showToast(title, icon, timer) {
  const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: timer,
    timerProgressBar: true,
  });

  Toast.fire({
    icon: icon,
    title: title
  });
}

function showAlert() {
  Swal.fire({
    title: "Good job!",
    text: "You clicked the button!",
    icon: "success"
  });
}