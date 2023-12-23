$(document).ready(function () {
  let antrianSocket = io("/antrian");
  let jadwalSocket = io("/jadwal");
  antrianSocket.on("new_antrian", function (data) {
    antrianTable.clear().draw();
    data.forEach(function (row, index) {
      antrianTable.row
        .add([row.poli, row.jumlah_pendaftar, row.dalam_antrian])
        .draw(false);
    });
  });

  if (typeof globalMessage !== "undefined") {
    showToast(globalMessage, "success", 3000);
  }

  let jadwalTable = $("#jadwalTable").DataTable({
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
      url: "/api/jadwal",
      dataFilter: function (data) {
        let json = jQuery.parseJSON(data);
        json.recordsTotal = json.datatables.recordsTotal;
        json.recordsFiltered = json.datatables.recordsFiltered;

        return JSON.stringify(json); // return JSON string
      },
    },
    columns: [
      { data: "nama" },
      { data: "poli" },
      { data: "hari" },
      {
        data: null,
        render: function (data, type, row) {
          return row.jam_buka + " - " + row.jam_tutup;
        },
      },
    ],
  });

  jadwalSocket.on("new_jadwal", function () {
    jadwalTable.ajax.reload();
  });

  let antrianTable = $("#antrianTable").DataTable({
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
  });

  // Ambil data antrian hari ini
  $.ajax({
    url: "/api/antrian/today",
    type: "GET",
    success: function (data) {
      // Isi tabel antrian hari ini
      antrianTable.clear().draw();
      data.data.forEach(function (row, index) {
        antrianTable.row
          .add([row.poli, row.jumlah_pendaftar, row.dalam_antrian])
          .draw(false);
      });
    },
  });
});
