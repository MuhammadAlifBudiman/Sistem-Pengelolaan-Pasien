$(document).ready(function () {
  AOS.init();
});

async function sign_out() {
  await fetch("/api/logout", {
    method: "POST",
  });
  // $.removeCookie("mytoken", { path: "/" });
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
    position: "top-end",
    showConfirmButton: false,
    timer: timer,
    timerProgressBar: true,
  });

  Toast.fire({
    icon: icon,
    title: title,
  });
}

function showAlert() {
  Swal.fire({
    title: "Good job!",
    text: "You clicked the button!",
    icon: "success",
  });
}

// Function to format date from yyyy-mm-dd to dd-mm-yyyy
function formatDateString(dateString) {
  const [year, month, day] = dateString.split("-");
  return `${day}-${month}-${year}`;
}
