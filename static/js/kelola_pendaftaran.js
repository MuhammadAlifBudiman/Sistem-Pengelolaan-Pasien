function renderTable(data) {
  console.log(data);
  let table = $("#myTable").DataTable();
  table.clear().draw();

  for (let i = 0; i < data.length; i++) {
    let row = data[i];
    let statusButtons = "";

    if (row.status === "pending") {
      statusButtons = `
                        <button class="btn btn-primary btn-action" data-registration-id="${row._id}" data-status="approved">Approve</button>
                        <button class="btn btn-danger btn-action" data-registration-id="${row._id}" data-status="rejected">Reject</button>
                    `;
    } else if (row.status === "approved") {
      statusButtons = `
                        <button class="btn btn-success btn-action-done" data-registration-id="${row._id}" data-status="done">Done</button>
                    `;
    }

    table.row
      .add([
        row.no_urut,
        row.name,
        row.poli,
        row.tanggal,
        row.keluhan,
        `
                        <div class="btn-group" role="group">
                            ${statusButtons}
                        </div>
                    `,
      ])
      .draw(false);
  }
}

$(document).ready(function () {
  let myDataTable = $("#myTable").DataTable();

  // Menangani klik tombol action (Approve, Reject, Done)
  $(document).on("click", ".btn-action", function () {
    let registrationId = $(this).data("registration-id");
    let status = $(this).data("status");
    let btnClicked = $(this);

    // Kirim permintaan ke server untuk mengubah status
    $.ajax({
      url: "/update_status",
      method: "POST",
      data: { registrationId: registrationId, status: status },
      success: function (response) {
        console.log("Response from the server:", response);

        if (status === "approved") {
          console.log("Approved button clicked");
          btnClicked.closest("tr").find(".btn-action").hide();
          btnClicked.closest("tr").find(".btn-action-done").show();
          window.location.reload();
        } else if (status === "done") {
          console.log("Done button clicked");
          myDataTable.row(btnClicked.closest("tr")).remove().draw(false);
        } else if (status === "rejected") {
          console.log("Rejected button clicked");
          myDataTable.row(btnClicked.closest("tr")).remove().draw(false);
        }

        // Perbarui data antrian jika diterima dari server
        // renderTable(response.antrian_data);
      },

      error: function (error) {
        console.error("Gagal mengubah status:", error);
      },
    });
  });

  // Menangani klik tombol 'done'
  $(document).on("click", ".btn-action-done", function () {
    let registrationId = $(this).data("registration-id");
    let status = $(this).data("status");
    let btnClicked = $(this);

    // Kirim permintaan ke server untuk mengubah status
    $.ajax({
      url: "/update_status",
      method: "POST",
      data: { registrationId: registrationId, status: status },
      success: function (response) {
        console.log("Done button clicked");
        myDataTable.row(btnClicked.closest("tr")).remove().draw(false);

        // Perbarui data antrian jika diterima dari server
        // renderTable(response.antrian_data);
      },
      error: function (error) {
        console.error("Gagal mengubah status:", error);
      },
    });
  });
});

function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("Logged out!");
  window.location.href = "/";
}
