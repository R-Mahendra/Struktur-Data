from flask import Flask, render_template, request, redirect, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# ============================================================
# KONFIGURASI
# ============================================================
kategori = ["Kuliah", "Pribadi", "Project"]
FILE_NAME = "tasks.json"
tasks = []

# ============================================================
# LOAD DATA JSON
# ============================================================
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as f:
        tasks = json.load(f)
else:
    tasks = []


# ============================================================
# HELPER: SAVE JSON
# ============================================================
def save_tasks():
    with open(FILE_NAME, "w") as f:
        json.dump(tasks, f, indent=2)


# ============================================================
# HELPER: NORMALIZE TASK (fix data lama)
# ============================================================
def normalize_task(task):
    defaults = ["", "Kuliah", "", "Belum", "Low", "-", ""]
    while len(task) < 7:
        task.append(defaults[len(task)])
    return task


# ============================================================
# HELPER: BUILD TASK DICT
# ============================================================
def build_task_dict(i, task):
    task = normalize_task(task)
    overdue = False
    try:
        tanggal_task = datetime.strptime(task[2], "%Y-%m-%d").date()
        today = datetime.today().date()
        if task[3] == "Belum" and tanggal_task < today:
            overdue = True
        days_left = (tanggal_task - today).days
    except Exception:
        days_left = 0

    return {
        "id": i,
        "nama": task[0],
        "kategori": task[1],
        "tanggal": task[2],
        "status": task[3],
        "priority": task[4],
        "created_at": task[5],
        "notes": task[6],
        "overdue": overdue,
        "days_left": days_left,
    }


# ============================================================
# HALAMAN UTAMA
# ============================================================
@app.route("/")
def index():
    search = request.args.get("search", "").lower()
    filter_kat = request.args.get("kategori", "Semua")
    sort_by = request.args.get("sort", "tanggal")
    filter_prior = request.args.get("priority", "Semua")

    belum = []
    selesai = []

    for i, task in enumerate(tasks):
        normalize_task(task)
        nama = task[0]

        # Filter search
        if search and search not in nama.lower() and search not in task[6].lower():
            continue

        # Filter kategori
        if filter_kat != "Semua" and task[1] != filter_kat:
            continue

        # Filter priority
        if filter_prior != "Semua" and task[4] != filter_prior:
            continue

        data = build_task_dict(i, task)

        if task[3] == "Belum":
            belum.append(data)
        else:
            selesai.append(data)

    # Sorting
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    if sort_by == "priority":
        belum.sort(key=lambda x: priority_order.get(x["priority"], 3))
    elif sort_by == "tanggal":
        belum.sort(key=lambda x: x["tanggal"])
    elif sort_by == "nama":
        belum.sort(key=lambda x: x["nama"].lower())

    total_task = len(tasks)
    total_selesai = len(selesai)
    progress = int((total_selesai / total_task) * 100) if total_task > 0 else 0

    # Stats per kategori
    stats = {}
    for k in kategori:
        total_k = sum(1 for t in tasks if normalize_task(t) and t[1] == k)
        selesai_k = sum(1 for t in tasks if t[1] == k and t[3] == "Selesai")
        stats[k] = {"total": total_k, "selesai": selesai_k}

    # Overdue count
    overdue_count = sum(1 for t in belum if t["overdue"])

    return render_template(
        "index.html",
        kategori=kategori,
        belum=belum,
        selesai=selesai,
        total_task=total_task,
        total_belum=len(belum),
        total_selesai=total_selesai,
        progress=progress,
        search=search,
        filter_kat=filter_kat,
        filter_prior=filter_prior,
        sort_by=sort_by,
        stats=stats,
        overdue_count=overdue_count,
    )


# ============================================================
# TAMBAH TASK
# ============================================================
@app.route("/add", methods=["POST"])
def add():
    nama = request.form.get("nama", "").strip()
    kat = request.form.get("kategori", "Kuliah")
    tanggal = request.form.get("tanggal", "")
    priority = request.form.get("priority", "Low")
    notes = request.form.get("notes", "")

    if not nama or not tanggal:
        return redirect("/")

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    tasks.append([nama, kat, tanggal, "Belum", priority, created_at, notes])
    save_tasks()
    return redirect("/")


# ============================================================
# SELESAI / UNDO / HAPUS
# ============================================================
@app.route("/done/<int:id>")
def done(id):
    if 0 <= id < len(tasks):
        tasks[id][3] = "Selesai"
    save_tasks()
    return redirect("/")


@app.route("/undo/<int:id>")
def undo(id):
    if 0 <= id < len(tasks):
        tasks[id][3] = "Belum"
    save_tasks()
    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):
    if 0 <= id < len(tasks):
        tasks.pop(id)
    save_tasks()
    return redirect("/")


# ============================================================
# EDIT TASK
# ============================================================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if not (0 <= id < len(tasks)):
        return redirect("/")

    if request.method == "POST":
        tasks[id][0] = request.form.get("nama", "").strip()
        tasks[id][1] = request.form.get("kategori", "Kuliah")
        tasks[id][2] = request.form.get("tanggal", "")
        tasks[id][4] = request.form.get("priority", "Low")
        tasks[id][6] = request.form.get("notes", "")
        save_tasks()
        return redirect("/")

    task_data = build_task_dict(id, tasks[id])
    return render_template(
        "edit.html", task=tasks[id], task_data=task_data, kategori=kategori, id=id
    )


# ============================================================
# API: Stats JSON (untuk chart di frontend)
# ============================================================
@app.route("/api/stats")
def api_stats():
    result = []
    for k in kategori:
        total = sum(1 for t in tasks if len(t) > 1 and t[1] == k)
        selesai = sum(
            1 for t in tasks if len(t) > 3 and t[1] == k and t[3] == "Selesai"
        )
        result.append({"kategori": k, "total": total, "selesai": selesai})
    return jsonify(result)


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)
