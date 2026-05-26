// ========================
// AUTO-SAVE DRAFT FORM
// ========================

const formFields = ["nama", "kategori", "tanggal", "priority", "notes"];

// Save draft tiap user ngetik
formFields.forEach((field) => {
  const el = document.getElementById(field);
  if (!el) return;

  // Load draft lama
  el.value = localStorage.getItem(`draft_${field}`) || "";

  // Simpan tiap perubahan
  el.addEventListener("input", () => {
    localStorage.setItem(`draft_${field}`, el.value);
  });
});

// Clear draft setelah form di-submit
document.getElementById("task-form").addEventListener("submit", () => {
  formFields.forEach((f) => localStorage.removeItem(`draft_${f}`));
});


function saveToLocalStorage() {
  const tasks = [];

  // Ambil semua row task
  document.querySelectorAll("tbody tr").forEach((row) => {
    const cols = row.querySelectorAll("td");

    // Pastikan kolom cukup
    if (cols.length >= 5) {
      tasks.push({
        nama: cols[0].innerText,
        kategori: cols[1].innerText,
        tanggal: cols[2].innerText,
        priority: cols[3].innerText,
        notes: cols[4].innerText,
      });
    }
  });

  // Simpan ke localStorage
  localStorage.setItem("tasks", JSON.stringify(tasks));

  console.log("Saved to localStorage");
}

// Jalankan otomatis saat halaman load
saveToLocalStorage();
