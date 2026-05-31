import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_extras.dataframe_explorer import dataframe_explorer
from EVChoose import (
    criteriaLabels,
    criteriaColumns,
    cost_criteria,
    prepare_data,
    computeSValue,
    computeVValue,
    computeRank,
    hitung_prioritas,
)
from streamlit_sortables import sort_items


df, criteriaColumns = prepare_data()

if "user_vehicles" not in st.session_state:
    st.session_state.user_vehicles = []

original_items = [
    {'items': criteriaLabels}
]

# Helper: normalisasi bobot
def _manual_to_prioritas_df(raw: dict) -> pd.DataFrame:
    total = sum(raw.values()) or 1
    rows = []
    for label in criteriaLabels:
        w = raw[label] / total
        if label in cost_criteria:
            w *= -1
        rows.append({"Kriteria": label, "Bobot": w})
    return pd.DataFrame(rows)

def apply_dark_theme(ax, fig):
    fig.patch.set_facecolor("#0E1117")
    ax.set_facecolor("#0E1117")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for spine in ax.spines.values():
        spine.set_color("white")
    ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.3)


def get_combined_df(filtered_df, user_vehicles):
    """Gabungkan data sistem dengan data kustom user.
    Kolom '_source' ditambahkan di sini secara terpusat, bukan dari dict input.
    """
    base = filtered_df.copy()
    base["_source"] = "system"

    if not user_vehicles:
        return base

    # Buat user_df dari kolom kriteria + brand + model saja (tanpa _source)
    user_df = pd.DataFrame(user_vehicles)

    # Pastikan semua kolom kriteria ada, isi None jika ada yang kosong
    for col in (["brand", "model"] + criteriaColumns):
        if col not in user_df.columns:
            user_df[col] = None

    # Tambahkan _source khusus untuk data user
    user_df["_source"] = "user"

    # Samakan urutan kolom dengan base
    user_df = user_df[[c for c in base.columns if c in user_df.columns]]

    # Kolom yang ada di base tapi tidak di user_df → isi NaN
    for col in base.columns:
        if col not in user_df.columns:
            user_df[col] = None

    user_df = user_df[base.columns]  # paksa urutan kolom identik

    return pd.concat([base, user_df], ignore_index=True)


simple_style = """
.sortable-component {
    background-color: black;
    font-size: 16px;
    counter-reset: item;
}
.sortable-item {
    background-color: black;
    color: white;
}
"""

st.title("Pemilihan EV Terbaik")
st.empty()


# Filter brand
df['brand'] = df['brand'].astype(str)
brand_options = sorted(df["brand"].dropna().unique())

selected_brands = st.multiselect(
    "Filter brand",
    options=brand_options,
    default=[]
)
df_filter_brand = df.copy()

if selected_brands:
    df_filter_brand = df_filter_brand[df_filter_brand["brand"].isin(selected_brands)]

df_filter_brand = df_filter_brand.reset_index(drop=True)
df_numeric_only = df_filter_brand.select_dtypes(include=['number'])
df_filter_numeric = dataframe_explorer(df_numeric_only, case=False)
mask = df_filter_brand.index.isin(df_filter_numeric.index)
filtered_df = df_filter_brand[mask].reset_index(drop=True)


# Tambah kendaraan kustom
add_custom = st.toggle("Tambah kendaraan sendiri untuk dibandingkan", value=False)

if add_custom:
    st.subheader("Input kendaraan kustom")

    with st.expander("Tambah kendaraan baru", expanded=True):
        with st.form("form_kendaraan_baru"):
            col1, col2 = st.columns(2)
            with col1:
                custom_brand = st.text_input("Brand")
            with col2:
                custom_model = st.text_input("Model")

            # Input nilai untuk setiap kriteria
            custom_vals = {}
            cols = st.columns(2)
            for i, col in enumerate(criteriaColumns):
                label = criteriaLabels[i]
                with cols[i % 2]:
                    custom_vals[col] = st.number_input(
                        label, min_value=0.0, step=0.1, key=f"custom_{col}"
                    )

            submitted = st.form_submit_button("Simpan kendaraan")

            #validasi brand & model wajib diisi
            if submitted:
                if not custom_brand.strip() or not custom_model.strip():
                    st.error("Brand dan Model wajib diisi.")
                else:
                    #simpan tanpa "_source", ditambahkan nanti di get_combined_df
                    new_vehicle = {
                        "brand": custom_brand.strip(),
                        "model": custom_model.strip(),
                        **custom_vals,
                    }
                    st.session_state.user_vehicles.append(new_vehicle)
                    st.success(f"✅ {custom_brand} {custom_model} berhasil ditambahkan!")
                    st.rerun()

    # Tampilkan & kelola daftar kendaraan user
    if st.session_state.user_vehicles:
        st.write("Kendaraan kustom yang akan ikut dihitung:")
        for i, v in enumerate(st.session_state.user_vehicles):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(f"{v['brand']} — {v['model']}")
            with col2:
                if st.button("Hapus", key=f"del_{i}"):
                    st.session_state.user_vehicles.pop(i)
                    st.rerun()
    else:
        st.info("Belum ada kendaraan kustom. Tambahkan menggunakan form di atas.")


# Pilih metode bobot
input_method = st.selectbox(
    "Pilih metode input bobot:",
    options=["Drag & Drop Prioritas", "Slider", "Number Input"],
    help="Pilih cara Anda ingin menentukan bobot kriteria"
)

with st.form(key="priorities_form", enter_to_submit=True):
    st.write("Atur bobot prioritas kriteria:")

    if input_method == "Drag & Drop Prioritas":
        st.caption("Seret kriteria untuk mengurutkan prioritas (atas = prioritas tertinggi).")
        sorted_items = sort_items(original_items, multi_containers=True, custom_style=simple_style)
        slider_weights = None
        number_weights = None

    elif input_method == "Slider":
        st.caption("Geser slider untuk menentukan bobot tiap kriteria (0–100). Bobot akan dinormalisasi otomatis.")
        slider_weights = {}
        cols = st.columns(2)
        for i, label in enumerate(criteriaLabels):
            with cols[i % 2]:
                slider_weights[label] = st.slider(
                    label, min_value=0, max_value=100, value=50, step=1,
                    key=f"slider_{label}"
                )
        sorted_items = None
        number_weights = None

    else:
        st.caption("Masukkan bobot untuk tiap kriteria (0.0–1.0). Bobot akan dinormalisasi otomatis.")
        number_weights = {}
        cols = st.columns(2)
        for i, label in enumerate(criteriaLabels):
            with cols[i % 2]:
                number_weights[label] = st.number_input(
                    label,
                    min_value=0.0, max_value=1.0,
                    value=round(1 / len(criteriaLabels), 2),
                    step=0.05, format="%.2f",
                    key=f"num_{label}"
                )
        sorted_items = None
        slider_weights = None

    run_clicked = st.form_submit_button(label="Jalankan Proses SPK")


# Proses SPK
if run_clicked:

    # Validasi bobot
    if input_method == "Drag & Drop Prioritas":
        if sorted_items is None:
            st.error("Gagal membaca urutan prioritas. Silakan coba lagi.")
            st.stop()
        df_prioritas = hitung_prioritas(sorted_items)

    elif input_method == "Slider":
        if slider_weights is None or sum(slider_weights.values()) == 0:
            st.error("Semua bobot slider bernilai 0. Sesuaikan minimal satu slider.")
            st.stop()
        df_prioritas = _manual_to_prioritas_df(slider_weights)

    else:
        if number_weights is None or sum(number_weights.values()) == 0:
            st.error("Semua bobot bernilai 0. Masukkan setidaknya satu bobot.")
            st.stop()
        df_prioritas = _manual_to_prioritas_df(number_weights)

    bobot_series = df_prioritas.set_index("Kriteria")["Bobot"]
    weights = [bobot_series[label] for label in criteriaLabels]

    # Bangun combined_df, pisahkan _source sebelum dikirim ke fungsi hitung
    combined_df = get_combined_df(filtered_df, st.session_state.user_vehicles)

    # final_df untuk kalkulasi, hanya kolom identitas + kriteria (tanpa _source)
    # _source disimpan terpisah sebagai series, di-merge kembali setelah hitung
    source_series = combined_df["_source"].copy()  # simpan mapping index → source
    final_df = combined_df[["brand", "model"] + criteriaColumns].copy()

    # Tampilkan bobot
    bobot_display = {
        row["Kriteria"]: f"{abs(row['Bobot']) * 100:.2f}%"
        for _, row in df_prioritas.iterrows()
    }
    bobot_df = pd.DataFrame(list(bobot_display.items()), columns=['Kriteria', 'Bobot'])

    with st.expander("Lihat bobot"):
        st.table(bobot_df)
        fig, ax = plt.subplots(figsize=(8, 4))
        bobot_abs = df_prioritas['Bobot'].abs() * 100
        bars = ax.bar(df_prioritas["Kriteria"], bobot_abs, color="#FF4B4B")
        ax.bar_label(bars, fmt='%.1f%%', padding=3, label_type='center', color='white')
        ax.set_title("Bobot Prioritas Kriteria")
        ax.set_ylabel("Persentase (%)")
        apply_dark_theme(ax, fig)
        st.pyplot(fig)
        plt.close(fig)

    if final_df.empty:
        st.warning("Tidak ada data yang memenuhi kriteria filter.")
    else:
        final_df = final_df.reset_index(drop=True)

        # hitung S, final_df sudah bersih dari kolom "_source"
        final_df["S"] = computeSValue(final_df, criteriaColumns, weights)

        # merge _source kembali ke final_df setelah hitung S
        final_df["_source"] = source_series.values

        # helper label sumber yang human-readable
        def source_label(src):
            return "Kustom" if src == "user" else "Sistem"

        # Lihat nilai S
        with st.expander("Lihat nilai S"):
            df_s = (
                final_df[["brand", "model", "_source", "S"]]
                .copy()
                .sort_values("S", ascending=False)
                .reset_index(drop=True)
            )
            df_s["Sumber"] = df_s["_source"].apply(source_label)
            st.dataframe(
                df_s[["brand", "model", "Sumber", "S"]].set_index("brand"),
                use_container_width=True
            )

            top_s = df_s.head(10)
            fig, ax = plt.subplots(figsize=(8, 5))
            # warna berbeda untuk data user
            colors_s = ["#FFD700" if s == "user" else "#FF4B4B" for s in top_s["_source"]]
            ax.plot(top_s["model"], top_s["S"], marker="o", linewidth=2, color="#FF4B4B")
            ax.set_title("Perbandingan Top 10 Nilai S")
            ax.set_xlabel("Model EV")
            ax.set_ylabel("Nilai S")
            plt.xticks(rotation=30)
            apply_dark_theme(ax, fig)
            st.pyplot(fig)
            plt.close(fig)

        # Hitung V
        final_df["V"] = computeVValue(final_df)

        # Lihat nilai V
        with st.expander("Lihat nilai V"):
            df_v = (
                final_df[["brand", "model", "_source", "V"]]
                .copy()
                .sort_values("V", ascending=False)
                .reset_index(drop=True)
            )
            df_v["Sumber"] = df_v["_source"].apply(source_label)
            st.dataframe(
                df_v[["brand", "model", "Sumber", "V"]].set_index("brand"),
                use_container_width=True
            )

        # Perankingan
        # computeRank menghasilkan DataFrame baru, re-merge _source berdasarkan brand+model
        finalRank = computeRank(final_df)

        # Buat lookup brand+model → _source dari final_df
        source_lookup = (
            final_df[["brand", "model", "_source"]]
            .drop_duplicates(subset=["brand", "model"])
            .set_index(["brand", "model"])["_source"]
        )

        # tambahkan kembali kolom _source ke finalRank
        finalRank["_source"] = finalRank.apply(
            lambda r: source_lookup.get((r["brand"], r["model"]), "system"),
            axis=1
        )
        finalRank["Sumber"] = finalRank["_source"].apply(source_label)

        # highlight_user pakai kolom "_source" yang sudah benar ada
        def make_highlighter(source_col="_source"):
            def highlight_user(row):
                if row.get(source_col, "system") == "user":
                    return ["background-color: #1a3a1a; color: #7fff7f"] * len(row)
                return [""] * len(row)
            return highlight_user

        top10 = finalRank.head(10).copy()
        display_rank = (
            top10
            .astype({"Rank": int})
            [["Rank", "brand", "model", "Sumber", "V"]]
            .set_index("Rank")
        )

        st.subheader("Top 10 Ranking EV")

        # Periksa apakah ada data user di top 10
        user_in_top10 = top10[top10["_source"] == "user"]
        if not user_in_top10.empty:
            nama_user = ", ".join(
                f"{r['brand']} {r['model']} (Rank #{int(r['Rank'])})"
                for _, r in user_in_top10.iterrows()
            )
            st.success(f"Kendaraan kustom masuk top 10: **{nama_user}**")
        else:
            # Cari rank kendaraan user di luar top 10
            user_ranks = finalRank[finalRank["_source"] == "user"]
            if not user_ranks.empty:
                nama_user = ", ".join(
                    f"{r['brand']} {r['model']} (Rank #{int(r['Rank'])} dari {len(finalRank)})"
                    for _, r in user_ranks.iterrows()
                )
                st.info(f"ℹ️ Kendaraan kustom: {nama_user}")

        # highlight bekerja karena "_source" ada di display_rank sebelum di-drop index
        st.dataframe(
            display_rank.style.apply(make_highlighter(), axis=1),
            use_container_width=True
        )

        st.toast("Proses SPK selesai.")

        # Grafik ranking
        ranking_chart = top10.copy()
        fig, ax = plt.subplots(figsize=(8, 5))

        # warna bar berbeda untuk data user
        bar_colors = ["#FFD700" if s == "user" else "#3B82F6"
                      for s in ranking_chart["_source"]]

        bars = ax.barh(ranking_chart["model"], ranking_chart["V"], color=bar_colors)
        ax.bar_label(bars, fmt='%.4f', padding=5, label_type='center', color='white')
        ax.set_title("Top 10 Ranking EV ")
        ax.set_xlabel("Nilai V")
        ax.invert_yaxis()
        apply_dark_theme(ax, fig)
        st.pyplot(fig)
        plt.close(fig)
