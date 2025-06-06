// kelola_pendaftaran.js
//
// This script manages the patient registration page, including filtering, DataTable setup, real-time updates via SocketIO, and status actions (approve, reject, done).
//
//

$(document).ready(function () {
  // Add filter icon to card header, opens filter modal on click
  $(".card-header").append(
    '<i class="fa-solid fa-sliders fa-xl" data-bs-toggle="modal" data-bs-target="#filterModal" style="color: #091e3e; cursor: pointer"></i>'
  );

  // Initialize Select2 dropdowns for filter modal
  let listName = $("#name");
  listName.select2({
    dropdownParent: $("#filterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari nama pasien",
  });
  let listPoli = $("#poli");
  listPoli.select2({
    dropdownParent: $("#filterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari poli",
  });
  listTanggal = $("#tanggal");
  listTanggal.select2({
    dropdownParent: $("#filterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari tanggal",
  });

  // Fetch dropdown options for filters (name, poli, tanggal)
  fetchList(
    "#name",
    "/api/pendaftaran?status=pending&status=approved&name=name"
  );
  fetchList(
    "#poli",
    "/api/pendaftaran?status=pending&status=approved&poli=poli"
  );
  fetchList(
    "#tanggal",
    "/api/pendaftaran?status=pending&status=approved&tanggal=tanggal"
  );

  /**
   * Fetches list data for a dropdown filter via AJAX and populates it.
   * @param {string} selector - jQuery selector for the dropdown
   * @param {string} url - API endpoint to fetch data
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
   * Populates a dropdown with options.
   * @param {string} selector - jQuery selector for the dropdown
   * @param {Array} options - Array of option values
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

  // Apply filter button: reload DataTable and close modal
  $("#applyFilter").on("click", function () {
    myDataTable.ajax.reload();
    $("#filterModal").modal("hide"); // Close the modal
  });

  // Initialize SocketIO connection for real-time updates
  let socket = io.connect("/pendaftaran");

  // Initialize DataTable for registration data
  let myDataTable = $("#myTable").DataTable({
    deferRender: true, // Improves performance for large datasets
    serverSide: true, // Server-side processing
    processing: true, // Show processing indicator
    responsive: {
      details: {
        type: "column",
        target: "tr",
        renderer: function (api, rowIdx, columns) {
          // Custom renderer for responsive details
          let data = columns
            .map((col, i) => {
              return col.hidden
                ? '<tr data-dt-row="' +
                    col.rowIndex +
                    '" data-dt-column="' +
                    col.columnIndex +
                    '">' +
                    "<td class='fw-bold'>" +
                    col.title +
                    "</td> " +
                    "<td>" +
                    col.data +
                    "</td>" +
                    "</tr>"
                : "";
            })
            .join("");

          let table = document.createElement("table");
          table.innerHTML = data;

          return data ? table : false;
        },
      },
    },

    ajax: {
      url: "/api/pendaftaran?status=pending&status=approved",
      data: function (d) {
        // Add filter values to AJAX request
        d.name = listName.val();
        d.poli = listPoli.val();
        d.tanggal = listTanggal.val();
        let status_filter = $("input[name='status']:checked").val();
        d.status_filter = status_filter;
      },
      dataFilter: function (data) {
        // Adapt server response for DataTables
        let json = jQuery.parseJSON(data);
        json.recordsTotal = json.datatables.recordsTotal;
        json.recordsFiltered = json.datatables.recordsFiltered;
        return JSON.stringify(json); // return JSON string
      },
    },
    columns: [
      {
        data: null,
        render: function (data, type, row) {
          // Display queue number or dash
          return row.antrian || "-";
        },
      },
      { data: "name" },
      { data: "poli" },
      { data: "tanggal" },
      { data: "keluhan" },
      {
        data: null,
        render: function (data, type, row) {
          // Render action buttons based on status
          let statusButton = ``;
          if (row.status === "pending") {
            statusButton = `
                              <button class="btn btn-action btn-sm text-light" data-registration-id="${row._id}" data-status="approved" style='background-color: #06a3da'>Approve</button>
                              <button class="btn btn-action btn-sm text-light" data-registration-id="${row._id}" data-status="rejected" style='background-color: #091e3e'>Reject</button>
                          `;
          } else if (row.status === "approved") {
            statusButton = `
                              <button class="btn btn-success btn-sm btn-action-done" data-registration-id="${row._id}" data-status="done">Done</button>
                          `;
          }
          return statusButton;
        },
      },
    ],
    order: [[3, "asc"]], // Default order by date
  });

  // Listen for new registration events and reload table
  socket.on("new_pendaftaran", function () {
    showToast("Ada pendaftaran baru", "success", 3000);
    myDataTable.ajax.reload();
  });

  // Handle Approve/Reject button clicks
  $(document).on("click", ".btn-action", function () {
    let registrationId = $(this).data("registration-id");
    let status = $(this).data("status");

    // Send request to server to change status
    if (status === "approved") {
      confirmButton(`/api/pendaftaran/${registrationId}/approve`, myDataTable);
    } else if (status === "rejected") {
      confirmButton(`/api/pendaftaran/${registrationId}/reject`, myDataTable);
    }
  });

  // Handle Done button click
  $(document).on("click", ".btn-action-done", function () {
    let registrationId = $(this).data("registration-id");
    confirmButton(`/api/pendaftaran/${registrationId}/done`, myDataTable);
  });
});

/**
 * Clears all filter selections in the filter modal.
 */
function clearFilter() {
  let listName = $("#name");
  let listPoli = $("#poli");
  let listTanggal = $("#tanggal");
  listName.val(null).trigger("change");
  listPoli.val(null).trigger("change");
  listTanggal.val(null).trigger("change");
  $("input[name='status']").prop("checked", false);
}

/**
 * Shows a confirmation dialog and sends a POST request to update registration status.
 * @param {string} url - API endpoint for status update
 * @param {object} myDataTable - DataTable instance to reload after update
 */
function confirmButton(url, myDataTable) {
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
        $.ajax({
          url: url,
          method: "POST",
          success: function (response) {
            swal.fire({
              title: "Berhasil!",
              text: response.message,
              icon: "success",
            });
            myDataTable.ajax.reload();
          },
          error: function (error) {
            showToast("Gagal mengubah status", "error", 3000);
          },
        });
      }
    });
  // Style SweetAlert2 button
  $("button.swal2-default-outline").addClass("w-auto");
}
