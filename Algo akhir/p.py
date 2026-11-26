import psycopg2
from datetime import date

def koneksi():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="algo_akhir",
            user="postgres",
            password="Kal160207"
        )
        return conn
    except Exception as e:
        print("Koneksi database gagal:", e)
        return None

import hashlib
import json
import os
from datetime import date, datetime, timedelta

FILE_DATA = "ecocash_data.json"
LEBAR = 50
GARIS = "-" * LEBAR
GARIS_TEBAL = "=" * LEBAR
JUMLAH_PERINGKAT = 10


# ====================== 3.1 STRUKTUR DATA DAN PENYIMPANAN ======================
def enkripsi(teks):
    """Mengubah password menjadi hash SHA-256 agar tidak tersimpan apa adanya."""
    return hashlib.sha256(teks.encode("utf-8")).hexdigest()


def data_awal():
    """Isi awal data: satu akun admin dan tiga contoh jenis sampah."""
    return {
        "USERS": [
            {"Id_user": "U001", "Username": "admin", "Password": enkripsi("admin123"),
             "Nama_lengkap": "Administrator", "Role": "admin", "saldo": 0}
        ],
        "SAMPAH": [
            {"Id_sampah": "S01", "Nama_sampah": "Plastik botol", "Harga_per_kg": 2500},
            {"Id_sampah": "S02", "Nama_sampah": "Kertas/Kardus", "Harga_per_kg": 1500},
            {"Id_sampah": "S03", "Nama_sampah": "Logam/Kaleng", "Harga_per_kg": 4000},
        ],
        "SETORAN": [],
        "PENARIKAN": [],
    }


def simpan_data(data):
    """Menulis seluruh tabel ke berkas; ditulis ke berkas sementara dulu agar aman."""
    sementara = FILE_DATA + ".tmp"
    with open(sementara, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(sementara, FILE_DATA)


def muat_data():
    """Membaca tabel dari berkas; jika belum ada, dibuat dari data awal."""
    if not os.path.exists(FILE_DATA):
        data = data_awal()
        simpan_data(data)
        return data
    with open(FILE_DATA, encoding="utf-8") as f:
        return json.load(f)


# ====================== 3.2 FUNGSI BANTU DAN VALIDASI INPUT ====================
def rupiah(nilai):
    """Contoh: 281250 -> 'Rp 281.250'."""
    return "Rp " + f"{nilai:,}".replace(",", ".")


def cari(daftar, kolom, nilai):
    """Mengembalikan baris pertama yang kolomnya sama dengan nilai, atau None."""
    for baris in daftar:
        if baris[kolom] == nilai:
            return baris
    return None


def buat_id(awalan, daftar, kolom, panjang):
    """Membuat id berikutnya, misalnya S03 -> S04 atau STR0007 -> STR0008."""
    terbesar = 0
    for baris in daftar:
        terbesar = max(terbesar, int(baris[kolom][len(awalan):]))
    return awalan + str(terbesar + 1).zfill(panjang)


def minta_teks(pesan):
    """Meminta teks yang tidak boleh kosong."""
    while True:
        teks = input(pesan).strip()
        if teks:
            return teks
        print("Input tidak boleh kosong.")


def minta_pilihan(pesan, valid):
    """Meminta pilihan menu sampai sesuai dengan daftar pilihan yang valid."""
    while True:
        pilihan = input(pesan).strip()
        if pilihan in valid:
            return pilihan
        print("Pilihan tidak tersedia, coba lagi.")


def minta_angka(pesan, jenis=float):
    """Meminta angka lebih dari 0 (bilangan bulat atau desimal)."""
    while True:
        teks = input(pesan).strip().replace(",", ".")
        try:
            angka = jenis(teks)
        except ValueError:
            print("Masukkan angka yang valid.")
            continue
        if angka > 0:
            return angka
        print("Angka harus lebih dari 0.")


def minta_tanggal(pesan, format_tanggal="%Y-%m-%d", boleh_kosong=False):
    """Meminta tanggal; formatnya bisa harian, bulanan (%Y-%m), atau tahunan (%Y)."""
    while True:
        teks = input(pesan).strip()
        if teks == "" and boleh_kosong:
            return date.today()
        try:
            return datetime.strptime(teks, format_tanggal).date()
        except ValueError:
            print("Format tidak valid, ikuti contoh yang tertera.")


def bersihkan_layar():
    """Membersihkan layar console agar tampilan menu selalu rapi."""
    os.system("cls" if os.name == "nt" else "clear")


def jeda():
    """Menahan layar supaya hasil perintah sempat dibaca sebelum kembali ke menu."""
    input("\nTekan Enter untuk melanjutkan...")


def halaman(judul):
    """Membersihkan layar lalu menampilkan judul halaman dengan format seragam."""
    bersihkan_layar()
    print(GARIS_TEBAL)
    print(judul.center(LEBAR))
    print(GARIS_TEBAL)


def tampil_menu(judul, pilihan, keterangan=""):
    """Menampilkan menu seragam dari daftar (kode, teks) lalu meminta pilihan."""
    print(GARIS_TEBAL)
    print(judul.center(LEBAR))
    if keterangan:
        print(keterangan.center(LEBAR))
    print(GARIS_TEBAL)
    for kode, teks in pilihan:
        print(f"  [{kode}] {teks}")
    print(GARIS)
    return minta_pilihan("Pilih menu : ", [kode for kode, _ in pilihan])


# ====================== 3.3 REGISTRASI DAN LOGIN ===============================
def registrasi(data):
    halaman("REGISTRASI NASABAH")
    nama = minta_teks("Nama lengkap : ")
    while True:
        username = minta_teks("Username     : ").lower()
        if cari(data["USERS"], "Username", username):
            print("Username sudah dipakai, gunakan yang lain.")
        else:
            break
    while True:
        password = minta_teks("Password (min. 4 karakter) : ")
        if len(password) >= 4:
            break
        print("Password minimal 4 karakter.")
    data["USERS"].append({
        "Id_user": buat_id("U", data["USERS"], "Id_user", 3),
        "Username": username,
        "Password": enkripsi(password),
        "Nama_lengkap": nama,
        "Role": "nasabah",
        "saldo": 0,
    })
    simpan_data(data)
    print("Registrasi berhasil. Silakan login.")


def login(data):
    """Mengembalikan data pengguna jika username dan password cocok, selain itu None."""
    halaman("LOGIN")
    username = minta_teks("Username : ").lower()
    password = minta_teks("Password : ")
    pengguna = cari(data["USERS"], "Username", username)
    if pengguna and pengguna["Password"] == enkripsi(password):
        return pengguna
    print("Username atau password salah.")
    return None


# ====================== 3.4 PENGELOLAAN JENIS DAN HARGA SAMPAH =================
def tampil_sampah(data):
    print(f"\n{'Kode':<6}{'Jenis Sampah':<22}{'Harga/kg':>12}")
    print(GARIS)
    for s in data["SAMPAH"]:
        harga = rupiah(s["Harga_per_kg"])
        print(f"{s['Id_sampah']:<6}{s['Nama_sampah']:<22}{harga:>12}")


def tambah_sampah(data):
    nama = minta_teks("Nama jenis sampah : ")
    for s in data["SAMPAH"]:
        if s["Nama_sampah"].lower() == nama.lower():
            print("Jenis sampah tersebut sudah ada.")
            return
    harga = minta_angka("Harga per kg (Rp) : ", int)
    kode = buat_id("S", data["SAMPAH"], "Id_sampah", 2)
    data["SAMPAH"].append(
        {"Id_sampah": kode, "Nama_sampah": nama, "Harga_per_kg": harga})
    simpan_data(data)
    print(f"Jenis sampah ditambahkan dengan kode {kode}.")


def ubah_harga(data):
    sampah = cari(data["SAMPAH"], "Id_sampah", minta_teks("Kode sampah : ").upper())
    if not sampah:
        print("Kode sampah tidak ditemukan.")
        return
    sampah["Harga_per_kg"] = minta_angka("Harga baru per kg (Rp) : ", int)
    simpan_data(data)
    harga = rupiah(sampah["Harga_per_kg"])
    print(f"Harga {sampah['Nama_sampah']} diubah menjadi {harga}/kg.")


def hapus_sampah(data):
    sampah = cari(data["SAMPAH"], "Id_sampah", minta_teks("Kode sampah : ").upper())
    if not sampah:
        print("Kode sampah tidak ditemukan.")
        return
    if cari(data["SETORAN"], "Id_sampah", sampah["Id_sampah"]):
        print("Jenis sampah sudah pernah disetor sehingga tidak dapat dihapus.")
        return
    if minta_pilihan(f"Hapus {sampah['Nama_sampah']}? (y/n) : ", ("y", "n")) == "y":
        data["SAMPAH"].remove(sampah)
        simpan_data(data)
        print("Jenis sampah dihapus.")


def kelola_sampah(data):
    while True:
        bersihkan_layar()
        tampil_sampah(data)
        print()
        pilihan = tampil_menu("KELOLA JENIS & HARGA SAMPAH", [
            ("1", "Tambah Jenis Sampah"),
            ("2", "Ubah Harga"),
            ("3", "Hapus Jenis Sampah"),
            ("0", "Kembali"),
        ])
        if pilihan == "0":
            return
        print()
        if pilihan == "1":
            tambah_sampah(data)
        elif pilihan == "2":
            ubah_harga(data)
        else:
            hapus_sampah(data)
        jeda()


# ====================== 3.5 SETOR SAMPAH =======================================
def setor_sampah(data):
    halaman("SETOR SAMPAH")
    username = minta_teks("Username nasabah : ").lower()
    nasabah = cari(data["USERS"], "Username", username)
    if not nasabah or nasabah["Role"] != "nasabah":
        print("Nasabah tidak ditemukan.")
        return
    tampil_sampah(data)
    sampah = cari(data["SAMPAH"], "Id_sampah", minta_teks("Kode sampah : ").upper())
    if not sampah:
        print("Kode sampah tidak ditemukan.")
        return
    berat = minta_angka("Berat (kg) : ", float)
    tanggal = minta_tanggal("Tanggal YYYY-MM-DD (Enter = hari ini) : ",
                            boleh_kosong=True)

    nilai = int(round(berat * sampah["Harga_per_kg"]))
    nasabah["saldo"] += nilai
    data["SETORAN"].append({
        "Id_setoran": buat_id("STR", data["SETORAN"], "Id_setoran", 4),
        "Id_user": nasabah["Id_user"],
        "Tanggal": tanggal.isoformat(),
        "Id_sampah": sampah["Id_sampah"],
        "Berat_kg": berat,
        "Total_nilai": nilai,
    })
    simpan_data(data)
    print(GARIS)
    print(f"Nasabah         : {nasabah['Nama_lengkap']}")
    print(f"Jenis sampah    : {sampah['Nama_sampah']} ({berat:g} kg)")
    print(f"Nilai setoran   : {rupiah(nilai)}")
    print(f"Saldo terbaru   : {rupiah(nasabah['saldo'])}")


# ====================== 3.6 SALDO, RIWAYAT, DAN PENARIKAN ======================
def cek_saldo(pengguna):
    print(f"\nSaldo {pengguna['Nama_lengkap']} : {rupiah(pengguna['saldo'])}")


def riwayat_transaksi(data, pengguna):
    """Menggabungkan setoran dan penarikan pengguna, diurutkan dari tanggal terlama."""
    transaksi = []
    for s in data["SETORAN"]:
        if s["Id_user"] == pengguna["Id_user"]:
            jenis = cari(data["SAMPAH"], "Id_sampah", s["Id_sampah"])["Nama_sampah"]
            transaksi.append((s["Tanggal"], s["Id_setoran"],
                              f"Setor {jenis} {s['Berat_kg']:g} kg", s["Total_nilai"]))
    for p in data["PENARIKAN"]:
        if p["Id_user"] == pengguna["Id_user"]:
            transaksi.append((p["Tanggal"], p["Id_penarikan"], "Tarik saldo",
                              -p["Jumlah_penarikan"]))
    halaman("RIWAYAT TRANSAKSI")
    if not transaksi:
        print("Belum ada transaksi.")
        return
    print(f"{'Tanggal':<12}{'Keterangan':<32}{'Jumlah':>14}")
    print(GARIS)
    for tanggal, _, keterangan, jumlah in sorted(transaksi):
        tanda = "+" if jumlah > 0 else "-"
        print(f"{tanggal:<12}{keterangan:<32}{tanda + rupiah(abs(jumlah)):>14}")


def tarik_saldo(data, pengguna):
    cek_saldo(pengguna)
    if pengguna["saldo"] <= 0:
        print("Saldo kosong, belum ada yang dapat ditarik.")
        return
    jumlah = minta_angka("Jumlah penarikan (Rp) : ", int)
    if jumlah > pengguna["saldo"]:
        print("Penarikan ditolak: jumlah melebihi saldo.")
        return
    pengguna["saldo"] -= jumlah
    data["PENARIKAN"].append({
        "Id_penarikan": buat_id("TRK", data["PENARIKAN"], "Id_penarikan", 4),
        "Tanggal": date.today().isoformat(),
        "Id_user": pengguna["Id_user"],
        "Jumlah_penarikan": jumlah,
    })
    simpan_data(data)
    sisa = rupiah(pengguna["saldo"])
    print(f"Penarikan {rupiah(jumlah)} berhasil. Sisa saldo {sisa}.")


# ====================== 3.7 LAPORAN DAN PERINGKAT ==============================
def tentukan_periode():
    """Mengembalikan (tanggal_awal, tanggal_akhir) dalam format YYYY-MM-DD."""
    bersihkan_layar()
    pilihan = tampil_menu("PILIH PERIODE LAPORAN", [
        ("1", "Harian"),
        ("2", "Mingguan (Senin - Minggu)"),
        ("3", "Bulanan"),
        ("4", "Tahunan"),
        ("5", "Semua waktu"),
    ])
    print()
    if pilihan == "1":
        awal = akhir = minta_tanggal("Tanggal (YYYY-MM-DD) : ")
    elif pilihan == "2":
        acuan = minta_tanggal("Tanggal acuan (YYYY-MM-DD) : ")
        awal = acuan - timedelta(days=acuan.weekday())      # hari Senin
        akhir = awal + timedelta(days=6)                    # hari Minggu
    elif pilihan == "3":
        awal = minta_tanggal("Bulan (YYYY-MM) : ", "%Y-%m")
        bulan_depan = date(awal.year + awal.month // 12, awal.month % 12 + 1, 1)
        akhir = bulan_depan - timedelta(days=1)
    elif pilihan == "4":
        awal = minta_tanggal("Tahun (YYYY) : ", "%Y")
        akhir = date(awal.year, 12, 31)
    else:
        awal, akhir = date.min, date.max
    return awal.isoformat(), akhir.isoformat()


def setoran_periode(data, awal, akhir):
    """Menyaring setoran yang tanggalnya berada di antara awal dan akhir."""
    return [s for s in data["SETORAN"] if awal <= s["Tanggal"] <= akhir]


def tampil_periode(awal, akhir):
    if awal == date.min.isoformat():
        print("Periode : Semua waktu")
    else:
        print(f"Periode : {awal} s.d. {akhir}")


def laporan_rekap(data, setoran):
    total = {}                      # Id_sampah -> [total berat, total nilai]
    for s in setoran:
        jumlah = total.setdefault(s["Id_sampah"], [0.0, 0])
        jumlah[0] += s["Berat_kg"]
        jumlah[1] += s["Total_nilai"]
    print(f"{'Jenis Sampah':<22}{'Berat (kg)':>12}{'Total Nilai':>16}")
    print(GARIS)
    for id_sampah, (berat, nilai) in sorted(total.items()):
        nama = cari(data["SAMPAH"], "Id_sampah", id_sampah)["Nama_sampah"]
        print(f"{nama:<22}{berat:>12.2f}{rupiah(nilai):>16}")
    print(GARIS)
    print(f"{'TOTAL':<22}{sum(b for b, _ in total.values()):>12.2f}"
          f"{rupiah(sum(n for _, n in total.values())):>16}")


def laporan_nasabah_rajin(data, setoran):
    rekap = {}                  # Id_user -> [jumlah setoran, total berat, total nilai]
    for s in setoran:
        jumlah = rekap.setdefault(s["Id_user"], [0, 0.0, 0])
        jumlah[0] += 1
        jumlah[1] += s["Berat_kg"]
        jumlah[2] += s["Total_nilai"]
    peringkat = []
    for id_user, (kali, berat, nilai) in rekap.items():
        nama = cari(data["USERS"], "Id_user", id_user)["Nama_lengkap"]
        peringkat.append({"nama": nama, "kali": kali, "berat": berat, "nilai": nilai})
    # urut: setoran terbanyak, lalu berat terbesar, lalu nama
    peringkat.sort(key=lambda p: (-p["kali"], -p["berat"], p["nama"]))
    print(f"{'No':<4}{'Nasabah':<22}{'Setor':>6}{'Berat (kg)':>12}{'Total Nilai':>16}")
    print(GARIS)
    for no, p in enumerate(peringkat[:JUMLAH_PERINGKAT], start=1):
        nilai = rupiah(p["nilai"])
        print(f"{no:<4}{p['nama']:<22}{p['kali']:>6}{p['berat']:>12.2f}{nilai:>16}")


def laporan_sampah_terlaris(data, setoran):
    rekap = {}                  # Id_sampah -> [total berat, jumlah setoran, total nilai]
    for s in setoran:
        jumlah = rekap.setdefault(s["Id_sampah"], [0.0, 0, 0])
        jumlah[0] += s["Berat_kg"]
        jumlah[1] += 1
        jumlah[2] += s["Total_nilai"]
    peringkat = []
    for id_sampah, (berat, kali, nilai) in rekap.items():
        nama = cari(data["SAMPAH"], "Id_sampah", id_sampah)["Nama_sampah"]
        peringkat.append({"nama": nama, "berat": berat, "kali": kali, "nilai": nilai})
    # urut: berat terbesar, lalu setoran terbanyak, lalu nama
    peringkat.sort(key=lambda p: (-p["berat"], -p["kali"], p["nama"]))
    print(f"{'No':<4}{'Jenis Sampah':<22}{'Berat (kg)':>12}{'Setor':>6}"
          f"{'Total Nilai':>16}")
    print(GARIS)
    for no, p in enumerate(peringkat[:JUMLAH_PERINGKAT], start=1):
        nilai = rupiah(p["nilai"])
        print(f"{no:<4}{p['nama']:<22}{p['berat']:>12.2f}{p['kali']:>6}{nilai:>16}")


def menu_laporan(data):
    judul = {"1": "REKAP SETORAN PER JENIS SAMPAH",
             "2": "PERINGKAT NASABAH PALING RAJIN",
             "3": "PERINGKAT SAMPAH TERLARIS"}
    while True:
        bersihkan_layar()
        pilihan = tampil_menu("MENU LAPORAN", [
            ("1", "Rekap Setoran per Jenis Sampah"),
            ("2", "Peringkat Nasabah Paling Rajin"),
            ("3", "Peringkat Sampah Terlaris"),
            ("0", "Kembali"),
        ])
        if pilihan == "0":
            return
        awal, akhir = tentukan_periode()
        setoran = setoran_periode(data, awal, akhir)
        halaman(judul[pilihan])
        tampil_periode(awal, akhir)
        if not setoran:
            print("Tidak ada data setoran pada periode ini.")
        elif pilihan == "1":
            laporan_rekap(data, setoran)
        elif pilihan == "2":
            laporan_nasabah_rajin(data, setoran)
        else:
            laporan_sampah_terlaris(data, setoran)
        jeda()


# ====================== 3.8 PROGRAM UTAMA DAN MENU =============================
def menu_admin(data, pengguna):
    while True:
        bersihkan_layar()
        pilihan = tampil_menu("MENU ADMIN", [
            ("1", "Kelola Jenis & Harga Sampah"),
            ("2", "Setor Sampah"),
            ("3", "Laporan dan Peringkat"),
            ("0", "Logout"),
        ], f"Login sebagai: {pengguna['Nama_lengkap']}")
        if pilihan == "1":
            kelola_sampah(data)
        elif pilihan == "2":
            setor_sampah(data)
            jeda()
        elif pilihan == "3":
            menu_laporan(data)
        else:
            return


def menu_nasabah(data, pengguna):
    while True:
        bersihkan_layar()
        pilihan = tampil_menu("MENU NASABAH", [
            ("1", "Cek Saldo"),
            ("2", "Riwayat Transaksi"),
            ("3", "Tarik Saldo"),
            ("0", "Logout"),
        ], f"{pengguna['Nama_lengkap']} | Saldo {rupiah(pengguna['saldo'])}")
        if pilihan == "1":
            halaman("CEK SALDO")
            cek_saldo(pengguna)
        elif pilihan == "2":
            riwayat_transaksi(data, pengguna)
        elif pilihan == "3":
            halaman("TARIK SALDO")
            tarik_saldo(data, pengguna)
        else:
            return
        jeda()


def main():
    data = muat_data()
    try:
        while True:
            bersihkan_layar()
            pilihan = tampil_menu("ECOCASH", [
                ("1", "Login"),
                ("2", "Registrasi Nasabah"),
                ("0", "Keluar"),
            ], "Tukar Sampahmu Menjadi Uang")
            if pilihan == "0":
                print("Terima kasih telah menggunakan EcoCash.")
                return
            if pilihan == "2":
                registrasi(data)
                jeda()
                continue
            pengguna = login(data)
            if pengguna is None:
                jeda()
                continue
            if pengguna["Role"] == "admin":
                menu_admin(data, pengguna)
            else:
                menu_nasabah(data, pengguna)
    except (EOFError, KeyboardInterrupt):
        print("\nProgram dihentikan.")


if __name__ == "__main__":
    main()
