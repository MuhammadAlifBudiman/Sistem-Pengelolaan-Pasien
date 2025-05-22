// dashboard.js - Main dashboard logic for patient management system
// This script handles DataTables initialization, filter modals, dropdown population, export functions, and AJAX interactions for the dashboard page.

// On document ready, initialize UI components and event listeners
$(document).ready(function () {
  // Add Export button and filter icon to Pendaftaran card header
  $("#pendaftaran .card-header").prepend(
    '<button type="button" class="btn text-light" onclick="exportPendaftaran()" style="background-color: #06a3da; width: auto" id="btn-tambah">Export</button>'
  );
  $("#pendaftaran .card-header").append(
    '<i class="fa-solid fa-sliders fa-xl" data-bs-toggle="modal" data-bs-target="#daftarFilterModal" style="color: #091e3e; cursor: pointer"></i>'
  );
  // Add Export button and filter icon to Checkup card header
  $("#checkup .card-header").append(
    '<i class="fa-solid fa-sliders fa-xl" data-bs-toggle="modal" data-bs-target="#checkupFilterModal" style="color: #091e3e; cursor: pointer"></i>'
  );
  $("#checkup .card-header").prepend(
    '<button type="button" class="btn text-light" onclick="exportCheckup()" style="background-color: #06a3da; width: auto" id="btn-tambah">Export</button>'
  );
  // Add filter icon to Rekam Medis card header
  $("#rekam-medis .card-header").append(
    '<i class="fa-solid fa-sliders fa-xl" data-bs-toggle="modal" data-bs-target="#rekamFilterModal" style="color: #091e3e; cursor: pointer"></i>'
  );

  // Initialize Select2 dropdowns for filter modals
  // Pendaftaran filters
  $("#name-daftar").select2({
    dropdownParent: $("#daftarFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari nama pasien",
  });
  $("#poli-daftar").select2({
    dropdownParent: $("#daftarFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari poli",
  });
  $("#tanggal-daftar").select2({
    dropdownParent: $("#daftarFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari tanggal",
  });

  // Checkup filters
  $("#name-pasien").select2({
    dropdownParent: $("#checkupFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari nama pasien",
  });
  $("#name-dokter").select2({
    dropdownParent: $("#checkupFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari nama dokter",
  });
  $("#tanggal-checkup").select2({
    dropdownParent: $("#checkupFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari tanggal",
  });
  $("#poli-checkup").select2({
    dropdownParent: $("#checkupFilterModal"),
    dropdownAutoWidth: true,
    placeholder: "Cari poli",
  });

  // Rekam Medis filters
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

  // Populate dropdowns with data from API endpoints
  fetchList("#name-daftar", "/api/pendaftaran?name=name");
  fetchList("#poli-daftar", "/api/pendaftaran?poli=poli");
  fetchList("#tanggal-daftar", "/api/pendaftaran?tanggal=tanggal");

  fetchList("#name-pasien", "/api/checkup?name=name");
  fetchList("#name-dokter", "/api/checkup?dokter=dokter");
  fetchList("#tanggal-checkup", "/api/checkup?tanggal=tanggal");
  fetchList("#poli-checkup", "/api/checkup?poli=poli");

  fetchList("#nik-rekam", "/api/rekam_medis?nik=nik");
  fetchList("#name-rekam", "/api/rekam_medis?name=name");

  // Initialize DataTables for each main table
  // Pendaftaran table
  let myTable = $("#pendaftaranTable").DataTable({
    deferRender: true, // Improves performance for large datasets
    serverSide: true, // Data is loaded from server
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
      url: "/api/pendaftaran", // API endpoint for data
      data: function (d) {
        // Attach filter values to request
        d.name = $("#name-daftar").val();
        d.poli = $("#poli-daftar").val();
        d.tanggal = $("#tanggal-daftar").val();
        let status_filter = $("input[name='status-daftar']:checked").val();
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
          // Show queue number or dash
          return row.antrian || "-";
        },
      },
      { data: "name" },
      { data: "poli" },
      { data: "tanggal" },
      {
        data: "status",
      },
    ],
    order: [[3, "asc"]], // Default sort by date
  });

  // Checkup table initialization
  let checkupTable = $("#checkupTable").DataTable({
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
      url: "/api/checkup",
      data: function (d) {
        // Attach filter values
        d.name = $("#name-pasien").val();
        d.dokter = $("#name-dokter").val();
        d.tanggal = $("#tanggal-checkup").val();
        d.poli = $("#poli-checkup").val();
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
        orderable: false,
        searchable: false,
        render: function (data, type, row, meta) {
          // Show row number
          return meta.row + meta.settings._iDisplayStart + 1;
        },
      },
      { data: "tgl_periksa" },
      { data: "nama" },
      {
        data: null,
        render: function (data, type, row) {
          // Show doctor or fallback
          return row.dokter || "Belum ada dokter";
        },
      },
      { data: "poli" },
      { data: "keluhan" },
      {
        data: null,
        render: function (data, type, row) {
          // Show anamnesa or fallback
          return row.hasil_anamnesa || "Belum ada hasil anamnesa";
        },
      },
    ],
    order: [[1, "asc"]],
  });

  // Rekam Medis table initialization
  let rekamMedisTable = $("#rekamMedisTable").DataTable({
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
      url: "/api/rekam_medis",
      data: function (d) {
        // Attach filter values
        d.name = $("#name-rekam").val();
        d.nik = $("#nik-rekam").val();
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
        orderable: false,
        searchable: false,
        render: function (data, type, row, meta) {
          // Show row number
          return meta.row + meta.settings._iDisplayStart + 1;
        },
      },
      { data: "nik" },
      { data: "nama" },
      {
        data: null,
        orderable: false,
        searchable: false,
        render: function (data, type, row) {
          // Button to view medical record details
          return `<button class='btn text-light btn-lihat' data-bs-toggle='modal' data-bs-target='#lihatModal' data-rekammedis-nik='${row.nik}' style='background-color: #091e3e'>Lihat</button>`;
        },
      },
    ],
  });

  // Event listener for Rekam Medis 'Lihat' button
  $("#rekamMedisTable").on("click", ".btn-lihat", function () {
    let rekamMedisNik = $(this).data("rekammedis-nik");

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable("#list_checkup_user")) {
      $("#list_checkup_user").DataTable().destroy();
    }

    // Initialize DataTable for patient's checkup history
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
          orderable: false,
          searchable: false,
          render: function (data, type, row, meta) {
            // Show row number
            return meta.row + meta.settings._iDisplayStart + 1;
          },
        },
        { data: "tgl_periksa" },
        {
          data: null,
          render: function (data, type, row) {
            // Show doctor or fallback
            return row.dokter || "Belum ada dokter";
          },
        },
        { data: "poli" },
        { data: "keluhan" },
        {
          data: null,
          render: function (data, type, row) {
            // Show anamnesa or fallback
            return row.hasil_anamnesa || "Belum ada hasil anamnesa";
          },
        },
      ],
      order: [[1, "asc"]],
    });

    // Fetch and display patient details in modal
    $.ajax({
      url: `/api/rekam_medis/${rekamMedisNik}`,
      type: "GET",
      success: function (response) {
        // Populate modal with patient info
        $("#list-checkup").empty();
        $("#list-checkup").append(
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

  // Filter apply button event listeners: reload tables and close modals
  $("#applyFilterDaftar").on("click", function () {
    myTable.ajax.reload();
    $("#daftarFilterModal").modal("hide"); // Close the modal
  });
  $("#applyFilterCheckup").on("click", function () {
    checkupTable.ajax.reload();
    $("#checkupFilterModal").modal("hide"); // Close the modal
  });
  $("#applyFilterRekam").on("click", function () {
    rekamMedisTable.ajax.reload();
    $("#rekamFilterModal").modal("hide"); // Close the modal
  });
});

/**
 * Fetches dropdown options from API and populates the given selector
 * @param {string} selector - jQuery selector for dropdown
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
 * Populates a dropdown with options
 * @param {string} selector - jQuery selector for dropdown
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

// Filter clearing functions for each filter modal
/**
 * Clears all filters in Pendaftaran filter modal
 */
function clearFilterDaftar() {
  let listName = $("#name-daftar");
  let listPoli = $("#poli-daftar");
  let listTanggal = $("#tanggal-daftar");
  listName.val(null).trigger("change");
  listPoli.val(null).trigger("change");
  listTanggal.val(null).trigger("change");
  $("input[name='status-daftar']").prop("checked", false);
}

/**
 * Clears all filters in Checkup filter modal
 */
function clearFilterCheckup() {
  let listName = $("#name-pasien");
  let listDokter = $("#name-dokter");
  let listTanggal = $("#tanggal-checkup");
  let listPoli = $("#poli-checkup");
  listName.val(null).trigger("change");
  listDokter.val(null).trigger("change");
  listTanggal.val(null).trigger("change");
  listPoli.val(null).trigger("change");
}

/**
 * Clears all filters in Rekam Medis filter modal
 */
function clearFilterRekam() {
  let listNik = $("#nik-rekam");
  let listName = $("#name-rekam");
  listNik.val(null).trigger("change");
  listName.val(null).trigger("change");
}

/**
 * Exports pendaftaran data for the last 30 days
 * Opens download link in new window
 */
function exportPendaftaran() {
  let endDate = new Date();
  let startDate = new Date();
  startDate.setDate(startDate.getDate() - 30);
  startDate = formatDate(startDate);
  endDate = formatDate(endDate);
  let url = `/api/pendaftaran/export?startdate=${startDate}&enddate=${endDate}`;
  window.location.href = url;
}

/**
 * Exports checkup data for the last 30 days
 * Opens download link in new window
 */
function exportCheckup() {
  let endDate = new Date();
  let startDate = new Date();
  startDate.setDate(startDate.getDate() - 30);
  startDate = formatDate(startDate);
  endDate = formatDate(endDate);
  let url = `/api/checkup/export?startdate=${startDate}&enddate=${endDate}`;
  window.location.href = url;
}

/**
 * Formats a Date object as DD-MM-YYYY string
 * @param {Date} date - Date object
 * @returns {string} - Formatted date string
 */
function formatDate(date) {
  let d = new Date(date);
  let month = "" + (d.getMonth() + 1);
  let day = "" + d.getDate();
  let year = d.getFullYear();

  if (month.length < 2) month = "0" + month;
  if (day.length < 2) day = "0" + day;

  return [day, month, year].join("-");
}
