// riwayat_pendaftaran.js
// This script initializes and configures the DataTable for displaying the user's registration history.
// It uses server-side processing and custom rendering for responsive details.

$(document).ready(function () {
  // Initialize DataTables on the #myTable element
  let myTable = $("#myTable").DataTable({
    // Enable deferred rendering for performance
    deferRender: true,
    // Enable server-side processing (data is fetched from the server)
    serverSide: true,
    // Show a processing indicator while loading data
    processing: true,
    // Enable responsive mode with custom details renderer
    responsive: {
      details: {
        type: "column", // Use entire row as the control for showing details
        target: "tr", // Target table rows for details
        renderer: function (api, rowIdx, columns) {
          // Custom renderer for responsive details
          // Map each column to a table row if it's hidden
          let data = columns
            .map((col, i) => {
              // If the column data is an array (e.g., days), join into a string
              if (typeof col.data === "object") {
                let hari = col.data.join(", ");
                col.data = hari;
              }
              // Only render hidden columns
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

          // Return the table if there is data, otherwise return false
          return data ? table : false;
        },
      },
    },
    ajax: {
      // URL to fetch registration data for the current user
      url: "/api/pendaftaran/me",
      // Data filter to adapt the server response to DataTables format
      dataFilter: function (data) {
        let json = jQuery.parseJSON(data);
        // Map custom response fields to DataTables expected fields
        json.recordsTotal = json.datatables.recordsTotal;
        json.recordsFiltered = json.datatables.recordsFiltered;

        return JSON.stringify(json); // Return the modified JSON string
      },
    },
    columns: [
      {
        data: null, // No data field, this is for row numbering
        searchable: false, // Disable search for this column
        orderable: false, // Disable ordering for this column
        render: function (data, type, row, meta) {
          // Render row number based on current page and index
          return meta.row + meta.settings._iDisplayStart + 1;
        },
      },
      { data: "name" }, // Patient name
      { data: "nik" }, // Patient NIK (ID number)
      { data: "poli" }, // Clinic/Poli name
      { data: "tanggal" }, // Registration date
      { data: "status" }, // Registration status
    ],
    // Default ordering: by registration date ascending
    order: [[4, "asc"]],
  });
});
