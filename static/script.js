// Main script for initializing UI components and utility functions

// Initialize Animate On Scroll (AOS) library when the document is ready
$(document).ready(function () {
  AOS.init();
});

// DataTables global defaults: processing spinner, empty/zero messages, ajax error toast
if (window.jQuery && $.fn && $.fn.dataTable) {
  $.extend(true, $.fn.dataTable.defaults, {
    language: {
      processing:
        '<div class="datatable-processing-content">' +
        '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' +
        "<span>Memuat data...</span>" +
        "</div>",
      emptyTable: "Belum ada data",
      zeroRecords: "Data tidak ditemukan",
    },
  });
  // Suppress built-in alert; route errors through toast instead
  $.fn.dataTable.ext.errMode = "none";
  $(document).on("error.dt", function (e, settings, techNote, message) {
    console.error("DataTables error:", message);
    if (typeof showToast === "function") {
      showToast("Data gagal dimuat. Silakan coba lagi.", "error", 4000);
    }
  });
}

/**
 * Asynchronously logs out the current user by sending a POST request to the logout API endpoint.
 * On success, redirects the user to the homepage with a logout message.
 */
async function sign_out() {
  await fetch("/api/logout", {
    method: "POST",
  });

  window.location.href = `/?msg=You have been logged out.`;
}

/**
 * Displays a toast notification using SweetAlert2.
 * @param {string} title - The message to display in the toast.
 * @param {string} icon - The icon to display (e.g., 'success', 'error').
 * @param {number} timer - Duration in milliseconds before the toast disappears.
 */
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

/**
 * Shows a SweetAlert2 alert with a success message.
 */
function showAlert() {
  Swal.fire({
    title: "Good job!",
    text: "You clicked the button!",
    icon: "success",
  });
}

/**
 * Formats a date string from 'yyyy-mm-dd' to 'dd-mm-yyyy'.
 * @param {string} dateString - The date string in 'yyyy-mm-dd' format.
 * @returns {string} The formatted date string in 'dd-mm-yyyy' format.
 */
function formatDateString(dateString) {
  const [year, month, day] = dateString.split("-");
  return `${day}-${month}-${year}`;
}
