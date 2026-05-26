from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)

# ARRAY 1 DIMENSI
# Menyimpan kategori task
kategori = ["Kuliah", "Pribadi", "Project"]

# Nama file penyimpanan JSON
FILE_NAME = "tasks.json"

# ARRAY 2 DIMENSI
# Menyimpan semua data task
tasks = []


# =========================
# LOAD DATA JSON
# =========================
# Mengecek apakah file JSON ada
# Jika ada -> load data
# Jika tidak -> buat array kosong

if os.path.exists(FILE_NAME):

    with open(FILE_NAME, "r") as f:
        tasks = json.load(f)

else:
    tasks = []


# =========================
# FUNCTION SAVE JSON
# =========================
# Menyimpan data task ke file JSON


def save_tasks():

    with open(FILE_NAME, "w") as f:
        json.dump(tasks, f)


# =========================
# HALAMAN UTAMA
# =========================
# Menampilkan:
# - list task
# - statistik
# - search
# - overdue


@app.route("/")
def index():

    # Mengambil input search

    search = request.args.get("search", "").lower()

    # Array task belum selesai
    belum = []

    # Array task selesai
    selesai = []

    # Loop semua task
    for i, task in enumerate(tasks):

        # Fix data lama jika belum ada priority
        # Fix data lama
        if len(task) == 4:
            task.append("Low")
            task.append("-")
            task.append("Tidak ada catatan")

        elif len(task) == 5:
            task.append("-")
            task.append("Tidak ada catatan")

        elif len(task) == 6:
            task.append("Tidak ada catatan")

        nama = task[0]

        # Filter search
        if search and search not in nama.lower():
            continue

        overdue = False

        # Cek tanggal task
        tanggal_task = datetime.strptime(task[2], "%Y-%m-%d").date()
        today = datetime.today().date()

        # Cek overdue
        if task[3] == "Belum" and tanggal_task < today:
            overdue = True

        # Dictionary data task
        data = {
            "id": i,
            "nama": task[0],
            "kategori": task[1],
            "tanggal": task[2],
            "status": task[3],
            "priority": task[4],
            "created_at": task[5],
            "notes": task[6],
            "overdue": overdue,
        }

        # Pisahkan task selesai dan belum
        if task[3] == "Belum":
            belum.append(data)

        else:
            selesai.append(data)

    # HITUNG PERSENTASE
    total_task = len(tasks)

    total_selesai = len(selesai)

    if total_task > 0:
        progress = int((total_selesai / total_task) * 100)
    else:
        progress = 0

    # Render Tamplate
    return render_template(
        "index.html",
        kategori=kategori,
        belum=belum,
        selesai=selesai,
        total_task=len(tasks),
        total_belum=len(belum),
        total_selesai=len(selesai),
        progress=progress,
        search=search,
    )


# =========================
# TAMBAH TASK
# =========================
# Menambahkan task baru


@app.route("/add", methods=["POST"])
def add():

    nama = request.form["nama"]
    kategori_task = request.form["kategori"]
    tanggal = request.form["tanggal"]
    priority = request.form["priority"]
    notes = request.form["notes"]

    # Waktu task dibuat
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Validasi input kosong
    if nama.strip() == "":
        return redirect("/")

    # Menambah task ke array 2D
    tasks.append([nama, kategori_task, tanggal, "Belum", priority, created_at, notes])

    # Simpan JSON
    save_tasks()

    return redirect("/")


# =========================
# TASK SELESAI
# =========================
# Mengubah status task menjadi selesai


@app.route("/done/<int:id>")
def done(id):

    if 0 <= id < len(tasks):
        tasks[id][3] = "Selesai"

    save_tasks()

    return redirect("/")


# =========================
# UNDO TASK
# =========================
# Mengubah status task menjadi belum selesai


@app.route("/undo/<int:id>")
def undo(id):

    if 0 <= id < len(tasks):
        tasks[id][3] = "Belum"

    save_tasks()

    return redirect("/")


# =========================
# HAPUS TASK
# =========================
# Menghapus task berdasarkan ID


@app.route("/delete/<int:id>")
def delete(id):

    if 0 <= id < len(tasks):
        tasks.pop(id)

    save_tasks()

    return redirect("/")


# =========================
# EDIT TASK
# =========================
# Mengubah data task


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if request.method == "POST":

        tasks[id][0] = request.form["nama"]
        tasks[id][1] = request.form["kategori"]
        tasks[id][2] = request.form["tanggal"]
        tasks[id][4] = request.form["priority"]
        tasks[id][6] = request.form["notes"]

        save_tasks()

        return redirect("/")

    return render_template("edit.html", task=tasks[id], kategori=kategori, id=id)


# =========================
# MENJALANKAN FLASK
# =========================

if __name__ == "__main__":
    app.run(debug=True)
