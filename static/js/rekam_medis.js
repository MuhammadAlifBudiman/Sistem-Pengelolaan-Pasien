// rekam medis
// This script handles the Rekam Medis (Medical Records) page functionality.
// It includes DataTable initialization, filtering, CRUD operations for medical records, and dropdown population.

$(document).ready(function () {
  // Add filter icon to the card header and initialize Select2 dropdowns for NIK and Name filters
  $("#medis .card-header").append(
    // FontAwesome filter icon triggers the filter modal
    '<i class="fa-solid fa-sliders fa-xl" data-bs-toggle="modal" data-bs-target="#rekamFilterModal" style="color: #091e3e; cursor: pointer"></i>'
  );

  // Initialize Select2 for NIK and Name dropdowns in the filter modal
  $("#nik-rekam").select2({
    dropdownParent: $("#rekamFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari NIK",
  });
  $("#name-rekam").select2({
    dropdownParent: $("#rekamFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari nama pasien",
  });

  // Populate NIK and Name dropdowns with data from API
  fetchList("#nik-rekam", "/api/users/pasien?nik=nik");
  fetchList("#name-rekam", "/api/users/pasien?name=name");

  // Inisialisasi datatables
  // Initialize the main DataTable for Rekam Medis
  let rekam_medisTable = $("#rekam_medisTable").DataTable({
    deferRender: true, // Improves performance for large datasets
    serverSide: true, // Data is loaded from the server
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
      url: "/api/users/pasien", // API endpoint for patient data
      data: function (d) {
        // Add filter parameters to the AJAX request
        d.name = $("#name-rekam").val();
        d.nik = $("#nik-rekam").val();
        let status_filter = $("input[name='status-rekam']:checked").val();
        d.status_filter = status_filter;
      },
      dataFilter: function (data) {
        // Adjust the response to fit DataTables format
        let json = jQuery.parseJSON(data);
        json.recordsTotal = json.datatables.recordsTotal;
        json.recordsFiltered = json.datatables.recordsFiltered;

        return JSON.stringify(json); // return JSON string
      },
    },
    columns: [
      {
        data: null,
        orderable: false,
        searchable: false,
        render: function (data, type, row, meta) {
          // Show row number
          return meta.row + meta.settings._iDisplayStart + 1;
        },
      },
      { data: "name" }, // Patient name
      { data: "nik" }, // Patient NIK
      {
        data: null,
        orderable: false,
        searchable: false,
        render: function (data, type, row) {
          // Show 'Lihat' (View) or 'Buat' (Create) button depending on record existence
          if (row.has_rekam_medis) {
            return `<button class='btn btn-sm btn-lihat text-light' data-bs-toggle='modal' data-bs-target='#lihatModal' data-rekammedis-nik='${row.nik}' style='background-color: #091e3e'>Lihat</button>`;
          } else {
            return `<button class='btn btn-sm btn-buat text-light' data-bs-toggle='modal' data-bs-target='#buatModal' data-rekammedis-nik='${row.nik}' style='background-color: #06a3da'>Buat</button>`;
          }
        },
      },
    ],
    order: [[1, "asc"]], // Default sort by name
  });

  // Apply filter button event
  $("#applyFilterRekam").on("click", function () {
    rekam_medisTable.ajax.reload(); // Reload table with new filters
    $("#rekamFilterModal").modal("hide"); // Close the modal
  });

  // Event listener for 'Buat' (Create) button
  $("#rekam_medisTable").on("click", ".btn-buat", function (e) {
    let rekamMedisNik = $(this).data("rekammedis-nik");
    let listDokter = $("#list-dokter");
    // Initialize Select2 for doctor selection
    listDokter.select2({
      dropdownParent: $("#buatModal"),
      dropdownAutoWidth: true,
      placeholder: "--Silakan Pilih Dokter--",
    });

    // Populate doctor dropdown
    fetchList("#list-dokter", "/api/jadwal?nama=nama");

    // Handle form submission for creating a new medical record
    $("#buatrekam_medis")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();
        let no = $("#no").val();

        let formData = $(this).serializeArray();
        formData.push({ name: "nik", value: rekamMedisNik });
        formData.push({ name: "no", value: no });

        // Send POST request to create new record
        $.ajax({
          url: `/api/rekam_medis`,
          type: "POST",
          data: formData,
          success: function (response) {
            if (response.result === "failed") {
              showToast(response.message, "error", 3000);
              return;
            }
            showToast(response.message, "success", 3000);
            $("#buatrekam_medis")[0].reset();
            $("#buatModal").modal("hide");
            rekam_medisTable.ajax.reload();
          },
          error: function (error) {
            showToast(error.responseJSON.message, "error", 3000);
          },
        });
      });
  });

  // Event listener for 'Lihat' (View) button
  $("#rekam_medisTable").on("click", ".btn-lihat", function () {
    let rekamMedisNik = $(this).data("rekammedis-nik");

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable("#list_checkup_user")) {
      $("#list_checkup_user").DataTable().destroy();
    }

    // Initialize DataTable for checkup history of selected patient
    let list_checkup_user = $("#list_checkup_user").DataTable({
      deferRender: true,
      serverSide: true,
      processing: true,
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
        url: `/api/checkup/${rekamMedisNik}`,
        dataFilter: function (data) {
          // Adjust the response to fit DataTables format
          let json = jQuery.parseJSON(data);
          json.recordsTotal = json.datatables.recordsTotal;
          json.recordsFiltered = json.datatables.recordsFiltered;

          return JSON.stringify(json); // return JSON string
        },
      },
      columns: [
        {
          data: null,
          orderable: false,
          searchable: false,
          render: function (data, type, row, meta) {
            // Show row number
            return meta.row + meta.settings._iDisplayStart + 1;
          },
        },
        { data: "tgl_periksa" }, // Checkup date
        {
          data: null,
          render: function (data, type, row) {
            // Show doctor name or fallback
            return row.dokter || "Belum ada dokter";
          },
        },
        { data: "poli" }, // Poli/Department
        { data: "keluhan" }, // Complaint
        {
          data: null,
          render: function (data, type, row) {
            // Show anamnesis result or fallback
            return row.hasil_anamnesa || "Belum ada hasil anamnesa";
          },
        },
        {
          data: null,
          orderable: false,
          searchable: false,
          render: function (data, type, row) {
            // Edit button for checkup record
            return `<button class='btn btn-sm btn-edit text-light' data-bs-toggle='modal'        data-bs-target='#editModal' data-checkup-id='${row._id}' data-rekammedis-nik='${rekamMedisNik}' style='background-color: #06a3da'>Edit</button>`;
          },
        },
      ],
      order: [[1, "asc"]], // Default sort by checkup date
    });

    // Fetch and display patient Rekam Medis details
    $.ajax({
      url: `/api/rekam_medis/${rekamMedisNik}`,
      type: "GET",
      success: function (response) {
        // Populate Rekam Medis details section
        $("#rekam-medis").empty();
        $("#rekam-medis").append(
          `<div class="row">
          <div class="col-sm-3">
            <h1>Data Rekam Medis Pasien Klinik Google</h1>
          </div>
          <div class="col-sm fs-4">
            <div class="row d-flex align-items-center text-start">
              <div class="col-sm-3">
                <p>No Kartu </p>
              </div>
              <div class="col-sm">
                <p class="text-secondary">${response.data.no_kartu}</p>
              </div>
            </div>
            <div class="row d-flex align-items-center text-start">
              <div class="col-sm-3">
                <p>Nama</p>
              </div>
              <div class="col-sm">
                <p class="text-secondary">${response.data.nama}</p>
              </div>
            </div>
            <div class="row d-flex align-items-center text-start">
              <div class="col-sm-3">
                <p>NIK </p>
              </div>
              <div class="col-sm">
                <p class="text-secondary">${response.data.nik}</p>
              </div>
            </div>
          </div>
          <div class="col-sm fs-4">
            <div class="row d-flex align-items-center text-start">
              <div class="col-sm-3">
                <p>Umur </p>
              </div>
              <div class="col-sm">
                <p class="text-secondary">${response.data.umur}</p>
              </div>
            </div>
            <div class="row d-flex align-items-center text-start">
              <div class="col-sm-3">
                <p>Alamat </p>
              </div>
              <div class="col-sm">
                <p class="text-secondary">${response.data.alamat}</p>
              </div>
            </div>
            <div class="row d-flex align-items-center text-start">
              <div class="col-sm-3">
                <p>No Telp </p>
              </div>
              <div class="col-sm">
                <p class="text-secondary">${response.data.no_telp}</p>
              </div>
            </div>
          </div>
        </div>`
        );
      },
      error: function (error) {
        showToast(error.responseJSON.message, "error", 3000);
      },
    });
  });

  // Event listener for Edit buttons in checkup history
  $("#list_checkup_user").on("click", ".btn-edit", function () {
    let checkupId = $(this).data("checkup-id");
    let rekamMedisNik = $(this).data("rekammedis-nik");
    let editModal = $("#editModal");
    let listDokter = $("#list-edit-dokter");
    // Initialize Select2 for doctor selection in edit modal
    listDokter.select2({
      dropdownParent: $("#editModal"),
      dropdownAutoWidth: true,
      placeholder: "--Silakan Pilih Dokter--",
    });
    // Populate doctor dropdown
    fetchList("#list-edit-dokter", "/api/jadwal?nama=nama");

    // Fetch checkup data for editing
    $.ajax({
      url: `/api/checkup/${rekamMedisNik}/${checkupId}`,
      type: "GET",
      success: function (response) {
        // Set doctor and anamnesis fields in the edit modal
        editModal
          .find("#list-edit-dokter")
          .val(response.data.dokter)
          .trigger("change");
        editModal.find("#hasil_anamnesa").val(response.data.hasil_anamnesa);
        listDokter
          .data("select2")
          .$container.find(".select2-selection__placeholder")
          .text(response.data.dokter);
      },
      error: function (error) {
        showToast(error.responseJSON.message, "error", 3000);
      },
    });

    // Handle form submission for editing checkup
    editModal
      .find("#edit")
      .off("submit")
      .submit(function (e) {
        e.preventDefault();

        let formData = $(this).serializeArray();

        // Send POST request to update checkup
        $.ajax({
          url: `/api/checkup/${rekamMedisNik}/${checkupId}`,
          type: "POST",
          data: formData,
          success: function (response) {
            if (response.result === "failed") {
              showToast(response.message, "error", 3000);
              return;
            }
            showToast(response.message, "success", 3000);
            $("#list_checkup_user").DataTable().ajax.reload();

            // Reset the form
            editModal.find("#edit")[0].reset();

            // Close the modal
            editModal.modal("hide");
          },
          error: function (error) {
            showToast(error.responseJSON.message, "error", 3000);
          },
        });
      });
  });
});

/**
 * Generate a random 6-digit nomor rekam medis (medical record number) in the format XX-XX-XX
 * and set it to the input field with id 'no'.
 */
function generateNomorRekamMedis() {
  // Assuming 6-digit nomor rekam medis with the format XX-XX-XX
  var nomorRekamMedis = Array.from({ length: 3 }, () =>
    Math.floor(Math.random() * 100)
      .toString()
      .padStart(2, "0")
  ).join("-");

  // Set the generated nomor rekam medis to the input field
  document.getElementById("no").value = nomorRekamMedis;
}

/**
 * Fetch list data from the given URL and populate the dropdown specified by selector.
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
 * Clear all Rekam Medis filters (NIK, Name, and status radio buttons)
 */
function clearFilterRekam() {
  let listNik = $("#nik-rekam");
  let listName = $("#name-rekam");
  listNik.val(null).trigger("change");
  listName.val(null).trigger("change");
  $("input[name='status-rekam']").prop("checked", false);
}
