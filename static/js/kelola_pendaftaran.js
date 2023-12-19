$(document).ready(function () {
  let myDataTable = $("#myTable").DataTable({
    serverSide: true,
    processing: true,
    scrollX: true,
    ajax: "/api/pendaftaran?status=pending&status=approved",
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
      { data: "keluhan" },
      {
        data: null,
        render: function (data, type, row) {
          let statusButton = ``;
          if (row.status === "pending") {
            statusButton = `
                              <button class="btn btn-primary btn-action" data-registration-id="${row._id}" data-status="approved">Approve</button>
                              <button class="btn btn-danger btn-action" data-registration-id="${row._id}" data-status="rejected">Reject</button>
                          `;
          } else if (row.status === "approved") {
            statusButton = `
                              <button class="btn btn-success btn-action-done" data-registration-id="${row._id}" data-status="done">Done</button>
                          `;
          }
          return `
            <div class="btn-group" role="group">
                ${statusButton}
            </div>
          `;
        },
      },
    ],
    order: [[3, "asc"]],
  });

  // Menangani klik tombol action (Approve, Reject, Done)
  $(document).on("click", ".btn-action", function () {
    let registrationId = $(this).data("registration-id");
    let status = $(this).data("status");

    // Kirim permintaan ke server untuk mengubah status
    if (status === "approved") {
      $.ajax({
        url: `/api/pendaftaran/${registrationId}/approve`,
        method: "POST",
        success: function (response) {
          showToast(response.message, "success", 3000);
          myDataTable.ajax.reload();
        },
        error: function (error) {
          showToast("Gagal mengubah status", "error", 3000);
        },
      });
    }
    else if (status === "rejected") {
      $.ajax({
        url: `/api/pendaftaran/${registrationId}/reject`,
        method: "POST",
        success: function (response) {
          showToast(response.message, "success", 3000);
          myDataTable.ajax.reload();
        },
        error: function (error) {
          showToast("Gagal mengubah status", "error", 3000);
        },
      });
    }
  });

  // Menangani klik tombol 'done'
  $(document).on("click", ".btn-action-done", function () {
    let registrationId = $(this).data("registration-id");

    // Kirim permintaan ke server untuk mengubah status
    $.ajax({
      url: `/api/pendaftaran/${registrationId}/done`,
      method: "POST",
      success: function (response) {
        showToast(response.message, "success", 3000);
        myDataTable.ajax.reload();
      },
      error: function (error) {
        showToast("Gagal mengubah status", "error", 3000);
      },
    });
  });
});
