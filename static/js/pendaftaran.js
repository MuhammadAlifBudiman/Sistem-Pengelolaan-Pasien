$(document).ready(async function () {
  const response = await fetch("/api/antrian/check");
  const dataResponse = await response.json();
  if (dataResponse.data.has_pending_or_approved) {
    sessionStorage.setItem("formStatus", "pending");
  } else {
    // remove formstatus from session storage
    sessionStorage.removeItem("formStatus");
  }

  

  let listPoli = $("#poli");
  let uniquePoli = [];
  listPoli.select2({
    dropdownAutoWidth: true,
    placeholder: "--Silakan Pilih Poli--",
  });

  fetchList("#poli", "/api/jadwal?poli=poli");

  // Get today's date in the format YYYY-MM-DD
  let today = new Date().toISOString().split("T")[0];

  // Set the max attribute of the date input to today
  $("#tanggal").attr("min", today);
  // Fungsi untuk merender tabel berdasarkan data yang diberikan
  function renderTable(data) {
    let table = $(".card-body");
    // add class table-responsive to table
    table.addClass("table-responsive");

    let tbody = $("#antrian-container tbody");
    tbody.empty();

    data.forEach(function (item) {
      $("#antrian-container .card-header button").remove();
      $("#antrian-container .card-header").append(
        `<button class="btn text-light w-auto" onclick="confirmButton('/api/pendaftaran/${item._id}/cancel')" style="background-color: #091e3e;">Cancel</button>`
      );
      let row = $("<tr>");
      let antrian = item.antrian || "-";
      row.append(`<td>${antrian}</td>`);
      row.append(`<td>${item.name}</td>`);
      row.append(`<td>${item.nik}</td>`);
      row.append(`<td>${item.tanggal}</td>`);
      row.append(`<td>${item.status}</td>`);

      tbody.append(row);
    });

    toggleFormAndAntrian(
      data.some(
        (item) => item.status === "pending" || item.status === "approved"
      )
    );
  }

  // Fungsi untuk menampilkan atau menyembunyikan formulir dan antrian berdasarkan data
  function toggleFormAndAntrian(hasPendingOrApproved) {
    $("#formulir-container").toggle(!hasPendingOrApproved);
    $("#antrian-container").toggle(hasPendingOrApproved);
    $("#formulir-container-done-rejected").toggle(
      sessionStorage.getItem("formStatus") === "rejected" ||
        sessionStorage.getItem("formStatus") === "done"
    );
  }

  // Periksa sessionStorage saat halaman dimuat
  let formStatus = sessionStorage.getItem("formStatus");

  if (
    formStatus === "done" ||
    formStatus === "rejected" ||
    formStatus === null
  ) {
    toggleFormAndAntrian(false);
  } else {
    toggleFormAndAntrian(true);

    // Jika formulir sudah dikirim, ambil dan tampilkan data antrian
    if (formStatus === "pending" || formStatus === "approved") {
      $.ajax({
        type: "GET",
        url: "/api/antrian/me",
        success: function (data) {
          renderTable(data.data);
        },
        error: function () {
          showToast("Gagal memuat data antrian", "error", 3000);
        },
      });
    }
  }

  // Perbarui peristiwa klik untuk tombol kirim
  $(".btn-submit-form").click(function (event) {
    event.preventDefault();

    if (formStatus === "done" || formStatus === "rejected") {
      showToast(
        "Formulir telah terkirim. Anda tidak dapat mengirim formulir lagi.",
        "error",
        3000
      );
      return;
    }

    let poli = $("#poli").val();
    let tanggal = $("#tanggal").val();
    let keluhan = $("#keluhan").val();

    if (!poli) {
      showToast(
        "Harap pilih jenis poli sebelum mengirim formulir",
        "error",
        3000
      );
      return;
    }

    if (!tanggal) {
      showToast(
        "Harap pilih tanggal berobat sebelum mengirim formulir",
        "error",
        3000
      );
      return;
    }

    if (!keluhan) {
      showToast(
        "Harap isi keluhan Anda sebelum mengirim formulir",
        "error",
        3000
      );
      return;
    }

    let formData = {
      poli: poli,
      tanggal: formatDateString(tanggal),
      keluhan: keluhan,
    };

    // Permintaan Ajax untuk mengirim formulir
    $.ajax({
      type: "POST",
      url: "/api/pendaftaran",
      data: formData,
      success: function (data) {
        if (data.result === "failed") {
          showToast(data.message, "error", 3000);
          return;
        }
        let newStatus = "pending";
        showToast(data.message, "success", 3000);

        sessionStorage.setItem("formStatus", newStatus);
        toggleFormAndAntrian(true);
        // change object data.data to list data
        let listData = [];
        listData.push(data.data);
        renderTable(listData);
      },
      error: function () {
        showToast("Gagal mengirim formulir", "error", 3000);
      },
    });
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

function confirmButton(url){
  swal.fire({
    title: "Apa kamu yakin ?",
    text: "Tindakan ini tidak bisa dipulihkan!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Ya",
    confirmButtonColor: "#06a3da",
    cancelButtonText: "Tidak",
    cancelButtonColor: "#091e3e",
    reverseButtons: true
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        url: url,
        method: "POST",
        success: function (response) {
          swal.fire({
            title: "Berhasil!",
            text: response.message,
            icon: "success"
          });
          window.location.reload();
        },
        error: function (error) {
          showToast("Gagal mengubah status", "error", 3000);
        },
      });
      
    }
  });

  $("button.swal2-default-outline").addClass("w-auto");
}
