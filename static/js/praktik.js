// praktik.js - Jadwal Table Management Script
// This script manages the schedule (jadwal) table, including filtering, adding, editing, and deleting doctor schedules.
// It uses jQuery, DataTables, and Select2 for UI interactions and AJAX for server communication.

// Wait for the DOM to be fully loaded before executing the script
$(document).ready(function () {
  // Initialize Select2 for doctor name filter dropdown in the filter modal
  $("#name-jadwal").select2({
    dropdownParent: $("#jadwalFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari nama dokter",
  });
  // Initialize Select2 for poli filter dropdown in the filter modal
  $("#poli-jadwal").select2({
    dropdownParent: $("#jadwalFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari poli",
  });
  // Fetch doctor names and poli options for filter dropdowns
  fetchList("#name-jadwal", "/api/jadwal?nama=nama");
  fetchList("#poli-jadwal", "/api/jadwal?poli=poli");

  // Initialize DataTable for jadwalTable with server-side processing and custom rendering
  let jadwalTable = $("#jadwalTable").DataTable({
    deferRender: true, // Improves performance for large datasets
    serverSide: true, // Data is loaded from the server
    processing: true, // Show processing indicator
    responsive: {
      details: {
        type: "column",
        target: "tr",
        renderer: function (api, rowIdx, columns) {
          // Custom renderer for responsive details view
          let data = columns
            .map((col, i) => {
              if (typeof col.data === "object") {
                // Join array data (e.g., days) into a string
                let hari = col.data.join(", ");
                col.data = hari;
              }
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
      url: "/api/jadwal", // API endpoint for fetching jadwal data
      data: function (d) {
        // Add filter parameters to the AJAX request
        d.nama = $("#name-jadwal").val();
        d.poli = $("#poli-jadwal").val();
        // Create an array to store selected days
        let selectedDays = [];
        // Iterate through the checked checkboxes and add their values to the array
        $("input[name='hari-jadwal']:checked").each(function () {
          selectedDays.push($(this).val());
        });
        // Assign the array to the 'hari' property
        d.hari = selectedDays;
      },
      dataFilter: function (data) {
        // Adapt the server response to DataTables format
        let json = jQuery.parseJSON(data);
        json.recordsTotal = json.datatables.recordsTotal;
        json.recordsFiltered = json.datatables.recordsFiltered;
        return JSON.stringify(json); // return JSON string
      },
    },
    columns: [
      { data: "nama" }, // Doctor name
      { data: "poli" }, // Poli name
      { data: "hari" }, // Days available
      {
        data: null,
        render: function (data, type, row) {
          // Render opening and closing hours
          return row.jam_buka + " - " + row.jam_tutup;
        },
      },
      {
        data: null,
        orderable: false,
        searchable: false,
        render: function (data, type, row) {
          // Render Edit and Delete buttons with jadwal ID
          return `<button class='btn text-light btn-sm btn-edit' data-bs-toggle='modal'        data-bs-target='#editModal' data-jadwal-id='${row._id}' style='background-color: #06a3da'>Edit</button> <button class='btn btn-danger btn-sm btn-delete' data-bs-toggle='modal' data-bs-target='#deleteModal' data-jadwal-id='${row._id}' style='background-color: #091e3e'>Delete</button>`;
        },
      },
    ],
  });

  // Apply filter button: reload table and close filter modal
  $("#applyFilterJadwal").on("click", function () {
    jadwalTable.ajax.reload();
    $("#jadwalFilterModal").modal("hide"); // Close the modal
  });

  // Insert 'Tambah' (Add) button and filter icon into the jadwal card header
  $("#jadwal .card-header").prepend(
    '<button type="button" class="btn text-light" data-bs-toggle="modal" data-bs-target="#exampleModal" style="background-color: #06a3da; width: auto" id="btn-tambah">Tambah</button>'
  );
  $("#jadwal .card-header").append(
    '<i class="fa-solid fa-sliders fa-xl" data-bs-toggle="modal" data-bs-target="#jadwalFilterModal" style="color: #091e3e; cursor: pointer"></i>'
  );

  // When 'Tambah' button is clicked, initialize Select2 for poli dropdown in add modal
  $("#btn-tambah").click(function () {
    let listPoli = $("#listPoli"); // Array to store unique poli values
    listPoli.select2({
      tags: true,
      dropdownParent: $("#exampleModal"),
      dropdownAutoWidth: true,
      placeholder: "--Silakan Pilih Poli--",
    });
    fetchList("#listPoli", "/api/jadwal?poli=poli");
  });

  // Event listener for Add Jadwal form submission
  $("#tambahJadwal").submit(function (e) {
    e.preventDefault();
    let formData = $(this).serializeArray();
    // Send POST request to add new jadwal
    $.ajax({
      url: "/api/jadwal",
      type: "POST",
      data: formData,
      success: function (response) {
        if (response.result === "failed") {
          showToast(response.message, "error", 3000);
          return;
        }
        showToast(response.message, "success", 3000);
        jadwalTable.ajax.reload();
        // reset form
        $("#tambahJadwal")[0].reset();
        // close modal
        $("#exampleModal").modal("hide");
      },
      error: function (error) {
        showToast(error.responseJSON.message, "error", 3000);
      },
    });
  });

  // Event listener for Edit buttons in the jadwal table
  $("#jadwalTable").on("click", ".btn-edit", function () {
    let listPoli = $("#editlistPoli"); // Array to store unique poli values
    listPoli.select2({
      tags: true,
      dropdownParent: $("#editModal"),
      dropdownAutoWidth: true,
      placeholder: "--Silakan Pilih Poli--",
    });
    fetchList("#editlistPoli", "/api/jadwal?poli=poli");

    let jadwalId = $(this).data("jadwal-id");
    let editModal = $("#editModal");
    // Fetch jadwal data for the selected row
    $.ajax({
      url: `/api/jadwal/${jadwalId}`,
      type: "GET",
      success: function (response) {
        let jadwal = response.data;
        // populate the edit modal with jadwal data
        editModal.find("#nama").val(jadwal.nama);
        editModal.find("#editlistPoli").val(jadwal.poli).trigger("change");
        editModal.find("#jamBuka").val(jadwal.jam_buka);
        editModal.find("#jamTutup").val(jadwal.jam_tutup);
        // Clear all checkboxes first
        editModal.find("input[name='hari']").prop("checked", false);
        // Check the checkboxes based on the received values
        for (let i = 0; i < jadwal.hari.length; i++) {
          editModal
            .find(
              "input[name='hari'][value='" + jadwal.hari[i].toLowerCase() + "']"
            )
            .prop("checked", true);
        }
      },
      error: function (error) {
        showToast(error.responseJSON.message, "error", 3000);
      },
    });

    // Event listener for Edit Jadwal form submission
    editModal
      .find("#editJadwal")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();
        let formData = $(this).serializeArray();
        // Send POST request to update jadwal
        $.ajax({
          url: `/api/jadwal/${jadwalId}`,
          type: "POST",
          data: formData,
          success: function (response) {
            if (response.result === "failed") {
              showToast(response.message, "error", 3000);
              return;
            }
            showToast(response.message, "success", 3000);
            jadwalTable.ajax.reload();
            // Reset the form
            editModal.find("#editJadwal")[0].reset();
            // Close the modal
            editModal.modal("hide");
          },
          error: function (error) {
            showToast(error.responseJSON.message, "error", 3000);
          },
        });
      });
  });

  // Event listener for Delete buttons in the jadwal table
  $("#jadwalTable").on("click", ".btn-delete", function () {
    let jadwalId = $(this).data("jadwal-id");
    // Fetch jadwal data for confirmation
    $.ajax({
      url: `/api/jadwal/${jadwalId}`,
      type: "GET",
      success: function (response) {
        let jadwal = response.data;
        $("#deleteModal")
          .find("#deleteTitle")
          .text(`Yakin hapus data ${jadwal.nama}?`);
      },
      error: function (error) {
        showToast(error.responseJSON.message, "error", 3000);
      },
    });

    // Event listener for Delete Jadwal form submission
    $("#hapusJadwal")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();
        // Send DELETE request to remove jadwal
        $.ajax({
          url: `/api/jadwal/${jadwalId}`,
          type: "DELETE",
          success: function (response) {
            if (response.result === "failed") {
              showToast(response.message, "error", 3000);
              return;
            }
            showToast(response.message, "success", 3000);
            jadwalTable.ajax.reload();
            // Close the modal
            $("#deleteModal").modal("hide");
          },
          error: function (error) {
            showToast(error.responseJSON.message, "error", 3000);
          },
        });
      });
  });
});

/**
 * Fetch list of options for a dropdown selector via AJAX and populate it.
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
 * Populate a dropdown with options.
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

/**
 * Clear all filters in the jadwal filter modal.
 * Resets dropdowns and checkboxes to default state.
 */
function clearFilterJadwal() {
  let listName = $("#name-jadwal");
  let listPoli = $("#poli-jadwal");
  let listTanggal = $("#tanggal-jadwal");
  listName.val(null).trigger("change");
  listPoli.val(null).trigger("change");
  listTanggal.val(null).trigger("change");
  $("input[name='hari-jadwal']").prop("checked", false);
}
