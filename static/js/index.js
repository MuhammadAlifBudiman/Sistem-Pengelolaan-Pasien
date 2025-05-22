// Main script for handling patient queue and schedule management dashboard
// Uses jQuery, DataTables, and Socket.IO for real-time updates

$(document).ready(function () {
  // Initialize Socket.IO connection for patient queue (antrian)
  let antrianSocket = io("/antrian");
  // Initialize Socket.IO connection for schedule (jadwal)
  let jadwalSocket = io("/jadwal");

  // Listen for new queue data and update the queue table
  antrianSocket.on("new_antrian", function (data) {
    // Clear the queue table before adding new data
    antrianTable.clear().draw();
    // Populate the queue table with new data
    data.forEach(function (row, index) {
      antrianTable.row
        .add([row.poli, row.jumlah_pendaftar, row.dalam_antrian])
        .draw(false);
    });
  });

  // Show a toast message if globalMessage is defined (e.g., after an action)
  if (typeof globalMessage !== "undefined") {
    showToast(globalMessage, "success", 3000);
  }

  // Initialize DataTable for schedule (jadwal)
  let jadwalTable = $("#jadwalTable").DataTable({
    deferRender: true, // Improves performance for large data
    serverSide: true, // Data is loaded from the server
    processing: true, // Show processing indicator
    responsive: {
      details: {
        type: "column",
        target: "tr",
        // Custom renderer for responsive details
        renderer: function (api, rowIdx, columns) {
          // Map hidden columns to a details table
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

          // Create a table element for details
          let table = document.createElement("table");
          table.innerHTML = data;

          // Return the details table or false if no data
          return data ? table : false;
        },
      },
    },
    ajax: {
      url: "/api/jadwal", // API endpoint for schedule data
      dataFilter: function (data) {
        // Parse and adjust the server response for DataTables
        let json = jQuery.parseJSON(data);
        json.recordsTotal = json.datatables.recordsTotal;
        json.recordsFiltered = json.datatables.recordsFiltered;

        return JSON.stringify(json); // Return JSON string
      },
    },
    columns: [
      { data: "nama" }, // Doctor's name
      { data: "poli" }, // Clinic/department
      { data: "hari" }, // Days available
      {
        data: null,
        // Render opening and closing hours as a single string
        render: function (data, type, row) {
          return row.jam_buka + " - " + row.jam_tutup;
        },
      },
    ],
  });

  // Listen for new schedule data and reload the schedule table
  jadwalSocket.on("new_jadwal", function () {
    jadwalTable.ajax.reload();
  });

  // Initialize DataTable for patient queue (antrian)
  let antrianTable = $("#antrianTable").DataTable({
    responsive: {
      details: {
        type: "column",
        target: "tr",
        // Custom renderer for responsive details
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

          // Create a table element for details
          let table = document.createElement("table");
          table.innerHTML = data;

          // Return the details table or false if no data
          return data ? table : false;
        },
      },
    },
  });

  // Fetch today's queue data from the server
  $.ajax({
    url: "/api/antrian/today", // API endpoint for today's queue
    type: "GET",
    success: function (data) {
      // Fill the queue table with today's data
      antrianTable.clear().draw();
      data.data.forEach(function (row, index) {
        antrianTable.row
          .add([row.poli, row.jumlah_pendaftar, row.dalam_antrian])
          .draw(false);
      });
    },
  });
});
