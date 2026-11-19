import streamlit as st
import mysql.connector
import pandas as pd

# ==================================
# 1. FUNGSI KONEKSI DATABASE
# ==================================

def koneksi():
    db = mysql.connector.connect(
        host=st.secrets["connection"]["mysql"]["host"],
        port=int(st.secrets["connection"]["mysql"]["port"]),
        user=st.secrets["connection"]["mysql"]["username"],
        password=st.secrets["connection"]["mysql"]["password"],
        database=st.secrets["connection"]["mysql"]["database"],
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )
    return db


st.title("🎓 Aplikasi Data Mahasiswa")
st.write("Aplikasi CRUD menggunakan Python Streamlit dan MySQL")

# ==================================
# 2. MENU APLIKASI
# ==================================

menu = st.sidebar.selectbox(
    "Pilih Menu",
    [
        "Tambah Data",
        "Data Mahasiswa",
        "Cari Mahasiswa",
        "Edit Data",
        "Hapus Data"
    ]
)

# ==================================
# 3. TAMBAH DATA MAHASISWA
# ==================================

if menu == "Tambah Data":

    st.subheader("Tambah Data Mahasiswa")

    nim = st.text_input("NIM")
    nama = st.text_input("Nama Mahasiswa")

    ipk = st.number_input(
        "IPK", min_value=0.0, max_value=4.0, step=0.01
    )

    semester = st.number_input(
        "Semester", min_value=1, max_value=14, step=1
    )

    prodi = st.selectbox(
        "Program Studi",
        [
            "Sistem Informasi",
            "Teknik Informatika",
            "Teknologi Informasi"
        ]
    )

    if st.button("Simpan Data"):

        if not nim.strip() or not nama.strip():
            st.warning("NIM dan Nama harus diisi!")

        else:
            db = None
            try:
                db = koneksi()
                cursor = db.cursor()

                sql = """
                    INSERT INTO mahasiswa
                    (nim, nama, ipk, semester, program_studi)
                    VALUES (%s, %s, %s, %s, %s)
                """

                cursor.execute(
                    sql,
                    (nim, nama, ipk, semester, prodi)
                )

                db.commit()
                cursor.close()

                st.success("Data mahasiswa berhasil disimpan!")

            except mysql.connector.Error as e:
                st.error(f"Gagal menyimpan data: {e}")

            finally:
                if db and db.is_connected():
                    db.close()

# ==================================
# 4. MENAMPILKAN DATA MAHASISWA
# ==================================

elif menu == "Data Mahasiswa":

    st.subheader("Daftar Seluruh Mahasiswa")

    db = None
    try:
        db = koneksi()

        query = """
            SELECT nim, nama, ipk, semester, program_studi
            FROM mahasiswa
        """

        data = pd.read_sql(query, db)

        st.dataframe(data, use_container_width=True)

    except mysql.connector.Error as e:
        st.error(f"Gagal mengambil data: {e}")

    finally:
        if db and db.is_connected():
            db.close()

# ==================================
# 5. PENCARIAN DATA MAHASISWA
# ==================================

elif menu == "Cari Mahasiswa":

    st.subheader("Cari Data Mahasiswa")

    cari = st.text_input("Masukkan NIM atau Nama Mahasiswa")

    if st.button("Cari Data"):

        db = None
        try:
            db = koneksi()
            cursor = db.cursor()

            sql = """
                SELECT nim, nama, ipk, semester, program_studi
                FROM mahasiswa
                WHERE nim LIKE %s OR nama LIKE %s
            """

            nilai = ("%" + cari + "%", "%" + cari + "%")

            cursor.execute(sql, nilai)
            hasil = cursor.fetchall()

            if hasil:
                data = pd.DataFrame(
                    hasil,
                    columns=[
                        "NIM", "Nama", "IPK",
                        "Semester", "Program Studi"
                    ]
                )

                st.success("Data mahasiswa ditemukan!")
                st.dataframe(data, use_container_width=True)

            else:
                st.warning("Data mahasiswa tidak ditemukan!")

            cursor.close()

        except mysql.connector.Error as e:
            st.error(f"Gagal mencari data: {e}")

        finally:
            if db and db.is_connected():
                db.close()

# ==================================
# 6. EDIT DATA MAHASISWA
# ==================================

elif menu == "Edit Data":

    st.subheader("Edit Data Mahasiswa")

    db = None
    try:
        db = koneksi()
        cursor = db.cursor()

        cursor.execute("""
            SELECT nim, nama, ipk, semester, program_studi
            FROM mahasiswa
        """)

        data = cursor.fetchall()

        if data:

            pilihan = st.selectbox(
                "Pilih Mahasiswa",
                data,
                format_func=lambda x: f"{x[0]} - {x[1]}"
            )

            nim_lama = pilihan[0]

            st.write("### Form Edit Data")

            nim = st.text_input("NIM", value=pilihan[0])
            nama = st.text_input("Nama", value=pilihan[1])

            ipk = st.number_input(
                "IPK",
                min_value=0.0,
                max_value=4.0,
                value=float(pilihan[2]),
                step=0.01
            )

            semester = st.number_input(
                "Semester",
                min_value=1,
                max_value=14,
                value=int(pilihan[3]),
                step=1
            )

            daftar_prodi = [
                "Sistem Informasi",
                "Teknik Informatika",
                "Teknologi Informasi"
            ]

            prodi_lama = pilihan[4]

            if prodi_lama not in daftar_prodi:
                daftar_prodi.append(prodi_lama)

            prodi = st.selectbox(
                "Program Studi",
                daftar_prodi,
                index=daftar_prodi.index(prodi_lama)
            )

            if st.button("Update Data"):

                sql = """
                    UPDATE mahasiswa
                    SET nim=%s, nama=%s, ipk=%s,
                        semester=%s, program_studi=%s
                    WHERE nim=%s
                """

                cursor.execute(
                    sql,
                    (nim, nama, ipk, semester, prodi, nim_lama)
                )

                db.commit()
                st.success("Data mahasiswa berhasil diperbarui!")

        else:
            st.warning("Belum ada data mahasiswa.")

        cursor.close()

    except mysql.connector.Error as e:
        st.error(f"Gagal mengedit data: {e}")

    finally:
        if db and db.is_connected():
            db.close()

# ==================================
# 7. HAPUS DATA MAHASISWA
# ==================================

elif menu == "Hapus Data":

    st.subheader("Hapus Data Mahasiswa")

    db = None
    try:
        db = koneksi()
        cursor = db.cursor()

        cursor.execute("""
            SELECT nim, nama, ipk, semester, program_studi
            FROM mahasiswa
        """)

        data = cursor.fetchall()

        if data:

            pilihan = st.selectbox(
                "Pilih Mahasiswa yang akan dihapus",
                data,
                format_func=lambda x: f"{x[0]} - {x[1]}"
            )

            st.write("Data yang akan dihapus:")
            st.write("NIM:", pilihan[0])
            st.write("Nama:", pilihan[1])

            if st.button("Hapus Data"):

                cursor.execute(
                    "DELETE FROM mahasiswa WHERE nim=%s",
                    (pilihan[0],)
                )

                db.commit()
                st.success("Data mahasiswa berhasil dihapus!")

        else:
            st.warning("Belum ada data mahasiswa.")

        cursor.close()

    except mysql.connector.Error as e:
        st.error(f"Gagal menghapus data: {e}")

    finally:
        if db and db.is_connected():
            db.close()