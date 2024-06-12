import streamlit as st

def main():
    st.title("Academic Essay Generator")
    
    topic = st.text_input("Enter the topic:")
    journal = st.selectbox("Select the journal:", ["PubMed", "ArXiv"])

    if st.button("Generate Essay"):
        st.write("Generating essay...")

        st.write("No essay generated due to errors in fetching or processing papers.")

        st.write("No references available.")

if __name__ == "__main__":
    main()
