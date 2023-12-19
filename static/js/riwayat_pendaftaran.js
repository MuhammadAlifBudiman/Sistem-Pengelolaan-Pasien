$(document).ready(function () {
  // Inisialisasi DataTables
  let myTable = $("#myTable").DataTable({
    serverSide: true,
    processing: true,
    scrollX: true,
    ajax: "/api/pendaftaran/me",
    columns: [
      {
        data: null,
        searchable: false,
        orderable: false,
        render: function (data, type, row, meta) {
          return meta.row + meta.settings._iDisplayStart + 1;
        },
      },
      { data: "name" },
      { data: "nik" },
      { data: "poli" },
      { data: "tanggal" },
      { data: "status" },
    ],
    columnDefs: [
      { width: "20%", targets: 0 }, // Adjust the width as needed
      { width: "20%", targets: 1 },
      { width: "20%", targets: 2 },
      { width: "20%", targets: 3 },
      { width: "20%", targets: 4 },
      { width: "20%", targets: 5 },
    ],
    order: [[4, "asc"]],
  });
});
