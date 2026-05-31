import streamlit as st

st.set_page_config(layout="wide")

def developer_card(name, role, skills, image_url, bio):
    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(image_url, width="stretch")
        
        with col2:
            st.subheader(name)
            st.caption(f"🚀 {role}")
            st.write(f"**Skills:** {skills}")
        
        # Fitur detail lebih lanjut menggunakan expander
        with st.expander("Lihat Detail Profil"):
            st.write(bio)
            # st.button("Hubungi Developer", key=name)

st.title("Team Developer")

left_col, right_col = st.columns(2)

with left_col:
    developer_card(
        name="Nicolaus Narindra Lianto",
        role="Backend Developer",
        skills="ctrl C + ctrl V",
        image_url="https://www.w3schools.com/howto/img_avatar.png",
        bio="Semua deadline tak trabas asal Claude Pro"
    )

with right_col:
    developer_card(
        name="Muthia Umairah",
        role="Frontend Developer",
        skills="Deadline Solver Spek Bondowoso",
        image_url="https://www.w3schools.com/howto/img_avatar2.png",
        bio="Minat tidur dengan tenang 24 jam tanpa beban deadline"
    )