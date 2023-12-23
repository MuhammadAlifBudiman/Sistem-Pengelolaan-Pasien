$(document).ready(function () {
  // Inisialisasi DataTables
  let myTable = $("#myTable").DataTable({
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
              if (typeof col.data === "object") {
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
      url: "/api/checkup/me",
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
      { data: "poli" },
      {
        data: null,
        render: function (data, type, row) {
          return row.dokter || "Belum ada dokter";
        },
      },
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
});
