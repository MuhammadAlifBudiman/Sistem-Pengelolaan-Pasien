// Jadwal Table
$(document).ready(function () {
  $("#pendaftaran .card-header").append(
    '<i class="fa-solid fa-sliders fa-xl" data-bs-toggle="modal" data-bs-target="#daftarFilterModal" style="color: #091e3e; cursor: pointer"></i>'
  );
  $("#checkup .card-header").append(
    '<i class="fa-solid fa-sliders fa-xl" data-bs-toggle="modal" data-bs-target="#checkupFilterModal" style="color: #091e3e; cursor: pointer"></i>'
  );
  $("#rekam-medis .card-header").append(
    '<i class="fa-solid fa-sliders fa-xl" data-bs-toggle="modal" data-bs-target="#rekamFilterModal" style="color: #091e3e; cursor: pointer"></i>'
  );


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

  fetchList(
    "#name-daftar",
    "/api/pendaftaran?name=name"
  );
  fetchList(
    "#poli-daftar",
    "/api/pendaftaran?poli=poli"
  );
  fetchList(
    "#tanggal-daftar",
    "/api/pendaftaran?tanggal=tanggal"
  );

  fetchList(
    "#name-pasien",
    "/api/checkup?name=name"
  );
  fetchList(
    "#name-dokter",
    "/api/checkup?dokter=dokter"
  );
  fetchList(
    "#tanggal-checkup",
    "/api/checkup?tanggal=tanggal"
  );
  fetchList(
    "#poli-checkup",
    "/api/checkup?poli=poli"
  );

  fetchList(
    "#nik-rekam",
    "/api/rekam_medis?nik=nik"
  );
  fetchList(
    "#name-rekam",
    "/api/rekam_medis?name=name"
  );

  // Inisialisasi DataTables
  let myTable = $("#pendaftaranTable").DataTable({
    deferRender: true,
    serverSide: true,
    processing: true,
    responsive: {
      details: {
        type: "column",
        target: "tr",
        renderer: function (api, rowIdx, columns) {
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
      url: "/api/pendaftaran",
      data: function (d) {
        d.name = $("#name-daftar").val();
        d.poli = $("#poli-daftar").val();
        d.tanggal = $("#tanggal-daftar").val();
        let status_filter = $("input[name='status-daftar']:checked").val();
        d.status_filter = status_filter;
      },
      dataFilter: function (data) {
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
    order: [[3, "asc"]],
  });

  let checkupTable = $("#checkupTable").DataTable({
    deferRender: true,
    serverSide: true,
    processing: true,
    responsive: {
      details: {
        type: "column",
        target: "tr",
        renderer: function (api, rowIdx, columns) {
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
        d.name = $("#name-pasien").val();
        d.dokter = $("#name-dokter").val();
        d.tanggal = $("#tanggal-checkup").val();
        d.poli = $("#poli-checkup").val();
      },
      dataFilter: function (data) {
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
          return meta.row + meta.settings._iDisplayStart + 1;
        },
      },
      { data: "tgl_periksa" },
      { data: "nama" },
      {
        data: null,
        render: function (data, type, row) {
          return row.dokter || "Belum ada dokter";
        },
      },
      { data: "poli" },
      { data: "keluhan" },
      {
        data: null,
        render: function (data, type, row) {
          return row.hasil_anamnesa || "Belum ada hasil anamnesa";
        },
      },
    ],
    order: [[1, "asc"]],
  });
  let rekamMedisTable = $("#rekamMedisTable").DataTable({
    deferRender: true,
    serverSide: true,
    processing: true,
    responsive: {
      details: {
        type: "column",
        target: "tr",
        renderer: function (api, rowIdx, columns) {
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
        d.name = $("#name-rekam").val();
        d.nik = $("#nik-rekam").val();
        
      },
      dataFilter: function (data) {
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
          return `<button class='btn text-light btn-lihat' data-bs-toggle='modal' data-bs-target='#lihatModal' data-rekammedis-nik='${row.nik}' style='background-color: #091e3e'>Lihat</button>`;
        },
      },
    ],
  });


  // Event listener for Lihat button
  $("#rekamMedisTable").on("click", ".btn-lihat", function () {
    let rekamMedisNik = $(this).data("rekammedis-nik");

    // Destroy existing DataTable if it exists
    if ($.fn.DataTable.isDataTable("#list_checkup_user")) {
      $("#list_checkup_user").DataTable().destroy();
    }

    let list_checkup_user = $("#list_checkup_user").DataTable({
      deferRender: true,
      serverSide: true,
      processing: true,
      responsive: {
        details: {
          type: "column",
          target: "tr",
          renderer: function (api, rowIdx, columns) {
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
            return meta.row + meta.settings._iDisplayStart + 1;
          },
        },
        { data: "tgl_periksa" },
        {
          data: null,
          render: function (data, type, row) {
            return row.dokter || "Belum ada dokter";
          },
        },
        { data: "poli" },
        { data: "keluhan" },
        {
          data: null,
          render: function (data, type, row) {
            return row.hasil_anamnesa || "Belum ada hasil anamnesa";
          },
        },
      ],
      order: [[1, "asc"]],
    });

    $.ajax({
      url: `/api/rekam_medis/${rekamMedisNik}`,
      type: "GET",
      success: function (response) {
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

// Function to fetch list dropdown options
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

// Function to populate dropdown with options
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

// Function to clear all filters
function clearFilterDaftar() {
  let listName = $("#name-daftar");
  let listPoli = $("#poli-daftar");
  let listTanggal = $("#tanggal-daftar");
  listName.val(null).trigger("change");
  listPoli.val(null).trigger("change");
  listTanggal.val(null).trigger("change");
  $("input[name='status-daftar']").prop("checked", false);
}

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

function clearFilterRekam() {
  let listNik = $("#nik-rekam");
  let listName = $("#name-rekam");
  listNik.val(null).trigger("change");
  listName.val(null).trigger("change");
}
