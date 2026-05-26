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
