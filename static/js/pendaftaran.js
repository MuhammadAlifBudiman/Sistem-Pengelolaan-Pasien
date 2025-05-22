// pendaftaran.js - Handles patient registration and queue management UI logic
//
// This script manages the registration form, queue status, and interactions with the backend API for patient queueing.
// It uses jQuery and Select2 for UI, and SweetAlert2 for confirmation dialogs.

$(document).ready(async function () {
  // Check if the user has a pending or approved queue entry
  const response = await fetch("/api/antrian/check");
  const dataResponse = await response.json();
  if (dataResponse.data.has_pending_or_approved) {
    // If there is a pending/approved entry, set formStatus to 'pending' in sessionStorage
    sessionStorage.setItem("formStatus", "pending");
  } else {
    // Otherwise, remove formStatus from sessionStorage
    sessionStorage.removeItem("formStatus");
  }

  // Initialize Select2 dropdown for 'poli' (clinic department)
  let listPoli = $("#poli");
  let uniquePoli = [];
  listPoli.select2({
    dropdownAutoWidth: true,
    placeholder: "--Silakan Pilih Poli--",
  });

  // Fetch and populate the 'poli' dropdown list
  fetchList("#poli", "/api/jadwal?poli=poli");

  // Get today's date in YYYY-MM-DD format
  let today = new Date().toISOString().split("T")[0];

  // Set the minimum selectable date to today
  $("#tanggal").attr("min", today);

  /**
   * Render the queue table with the provided data
   * @param {Array} data - List of queue entries
   */
  function renderTable(data) {
    let table = $(".card-body");
    // Make table responsive
    table.addClass("table-responsive");

    let tbody = $("#antrian-container tbody");
    tbody.empty();

    data.forEach(function (item) {
      // Remove any existing cancel button and add a new one for each entry
      $("#antrian-container .card-header button").remove();
      $("#antrian-container .card-header").append(
        `<button class=\"btn text-light w-auto\" onclick=\"confirmButton('/api/pendaftaran/${item._id}/cancel')\" style=\"background-color: #091e3e;\">Cancel</button>`
      );
      let row = $("<tr>");
      let antrian = item.antrian || "-";
      row.append(`<td>${antrian}</td>`);
      row.append(`<td>${item.name}</td>`);
      row.append(`<td>${item.nik}</td>`);
      row.append(`<td>${item.tanggal}</td>`);
      row.append(`<td>${item.status}</td>`);

      tbody.append(row);
    });

    // Show/hide form and queue table based on status
    toggleFormAndAntrian(
      data.some(
        (item) => item.status === "pending" || item.status === "approved"
      )
    );
  }

  /**
   * Show or hide the registration form and queue table based on queue status
   * @param {boolean} hasPendingOrApproved - Whether there is a pending/approved queue
   */
  function toggleFormAndAntrian(hasPendingOrApproved) {
    $("#formulir-container").toggle(!hasPendingOrApproved);
    $("#antrian-container").toggle(hasPendingOrApproved);
    $("#formulir-container-done-rejected").toggle(
      sessionStorage.getItem("formStatus") === "rejected" ||
        sessionStorage.getItem("formStatus") === "done"
    );
  }

  // Get form status from sessionStorage
  let formStatus = sessionStorage.getItem("formStatus");

  // Show/hide form and queue table based on form status
  if (
    formStatus === "done" ||
    formStatus === "rejected" ||
    formStatus === null
  ) {
    toggleFormAndAntrian(false);
  } else {
    toggleFormAndAntrian(true);

    // If form is pending/approved, fetch and display the user's queue data
    if (formStatus === "pending" || formStatus === "approved") {
      $.ajax({
        type: "GET",
        url: "/api/antrian/me",
        success: function (data) {
          renderTable(data.data);
        },
        error: function () {
          showToast("Gagal memuat data antrian", "error", 3000);
        },
      });
    }
  }

  // Handle form submission
  $(".btn-submit-form").click(function (event) {
    event.preventDefault();

    // Prevent resubmission if already done or rejected
    let formStatus = sessionStorage.getItem("formStatus"); // re-fetch status on click
    if (formStatus === "done" || formStatus === "rejected") {
      showToast(
        "Formulir telah terkirim. Anda tidak dapat mengirim formulir lagi.",
        "error",
        3000
      );
      return;
    }

    // Get form values
    let poli = $("#poli").val();
    let tanggal = $("#tanggal").val();
    let keluhan = $("#keluhan").val();

    // Validate form fields
    if (!poli) {
      showToast(
        "Harap pilih jenis poli sebelum mengirim formulir",
        "error",
        3000
      );
      return;
    }

    if (!tanggal) {
      showToast(
        "Harap pilih tanggal berobat sebelum mengirim formulir",
        "error",
        3000
      );
      return;
    }

    if (!keluhan) {
      showToast(
        "Harap isi keluhan Anda sebelum mengirim formulir",
        "error",
        3000
      );
      return;
    }

    // Prepare form data for submission
    let formData = {
      poli: poli,
      tanggal: formatDateString(tanggal),
      keluhan: keluhan,
    };

    // Submit registration form via AJAX
    $.ajax({
      type: "POST",
      url: "/api/pendaftaran",
      data: formData,
      success: function (data) {
        if (data.result === "failed") {
          showToast(data.message, "error", 3000);
          return;
        }
        let newStatus = "pending";
        showToast(data.message, "success", 3000);

        // Update form status and UI
        sessionStorage.setItem("formStatus", newStatus);
        toggleFormAndAntrian(true);
        // Convert single data object to list for rendering
        let listData = [];
        listData.push(data.data);
        renderTable(listData);
      },
      error: function () {
        showToast("Gagal mengirim formulir", "error", 3000);
      },
    });
  });
});

/**
 * Fetch dropdown options from API and populate the selector
 * @param {string} selector - jQuery selector for the dropdown
 * @param {string} url - API endpoint to fetch options
 */
function fetchList(selector, url) {
  $.ajax({
    url: url,
    type: "GET",
    success: function (response) {
      data = response.data;
      populateDropdown(selector, data);
    },
    error: function (error) {
      showToast("Error", "error", 3000);
    },
  });
}

/**
 * Populate a dropdown with options
 * @param {string} selector - jQuery selector for the dropdown
 * @param {Array} options - List of options to add
 */
function populateDropdown(selector, options) {
  let dropdown = $(selector);
  dropdown.empty();
  dropdown.append('<option value="">Semua</option>');
  for (let i = 0; i < options.length; i++) {
    dropdown.append(
      '<option value="' + options[i] + '">' + options[i] + "</option>"
    );
  }
}

/**
 * Show a confirmation dialog and send a cancel request if confirmed
 * @param {string} url - API endpoint to cancel the registration
 */
function confirmButton(url) {
  swal
    .fire({
      title: "Apa kamu yakin ?",
      text: "Tindakan ini tidak bisa dipulihkan!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Ya",
      confirmButtonColor: "#06a3da",
      cancelButtonText: "Tidak",
      cancelButtonColor: "#091e3e",
      reverseButtons: true,
    })
    .then((result) => {
      if (result.isConfirmed) {
        // Send cancel request if confirmed
        $.ajax({
          url: url,
          method: "POST",
          success: function (response) {
            swal.fire({
              title: "Berhasil!",
              text: response.message,
              icon: "success",
            });
            window.location.reload();
          },
          error: function (error) {
            showToast("Gagal mengubah status", "error", 3000);
          },
        });
      }
    });

  // Style the SweetAlert2 button
  $("button.swal2-default-outline").addClass("w-auto");
}
