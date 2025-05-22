// Documentation for riwayat_checkup.js
// This script initializes a DataTable for displaying patient checkup history with server-side processing and responsive details.

$(document).ready(function () {
  // Initialize DataTables on the #myTable element
  let myTable = $("#myTable").DataTable({
    // Enable deferred rendering for performance
    deferRender: true,
    // Enable server-side processing (data fetched from server)
    serverSide: true,
    // Show processing indicator while loading
    processing: true,
    // Enable responsive design with custom details renderer
    responsive: {
      details: {
        type: "column", // Show details in a column
        target: "tr", // Target table rows for details
        renderer: function (api, rowIdx, columns) {
          // Custom renderer for responsive details
          let data = columns
            .map((col, i) => {
              // If column data is an object (e.g., array of days), join as string
              if (typeof col.data === "object") {
                let hari = col.data.join(", ");
                col.data = hari;
              }
              // Only render hidden columns in the details view
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

          // Create a table element for the details
          let table = document.createElement("table");
          table.innerHTML = data;

          // Return the table if there is data, otherwise false
          return data ? table : false;
        },
      },
    },
    ajax: {
      // URL to fetch data for the table
      url: "/api/checkup/me",
      // Data filter to adapt server response to DataTables format
      dataFilter: function (data) {
        let json = jQuery.parseJSON(data);
        // Map custom response fields to DataTables expected fields
        json.recordsTotal = json.datatables.recordsTotal;
        json.recordsFiltered = json.datatables.recordsFiltered;

        return JSON.stringify(json); // Return JSON string
      },
    },
    columns: [
      {
        // First column: row number (not orderable/searchable)
        data: null,
        orderable: false,
        searchable: false,
        render: function (data, type, row, meta) {
          // Calculate and return the row number
          return meta.row + meta.settings._iDisplayStart + 1;
        },
      },
      { data: "tgl_periksa" }, // Date of checkup
      { data: "poli" }, // Clinic/Poli name
      {
        // Doctor name (or fallback if not available)
        data: null,
        render: function (data, type, row) {
          return row.dokter || "Belum ada dokter";
        },
      },
      { data: "keluhan" }, // Complaint
      {
        // Anamnesis result (or fallback if not available)
        data: null,
        render: function (data, type, row) {
          return row.hasil_anamnesa || "Belum ada hasil anamnesa";
        },
      },
    ],
    // Default ordering by checkup date ascending
    order: [[1, "asc"]],
  });
});
