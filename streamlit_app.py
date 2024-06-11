import streamlit as st
from essay_writer import generate_essay_and_references  

def main():
    st.title("Academic Essay Generator")
    
    topic = st.text_input("Enter the topic:")
    journal = st.selectbox("Select the journal:", ["PubMed", "ArXiv"])

    if st.button("Generate Essay"):
        st.write("Generating essay...")
        '''essay, references = generate_essay_and_references(topic, journal)'''

        if essay:
            st.subheader("Essay:")
            st.write(essay)
        else:
            st.write("No essay generated due to errors in fetching or processing papers.")

        st.subheader("References:")
        if references:
            for ref in references:
                st.write(ref)
        else:
            st.write("No references available.")

if __name__ == "__main__":
    main()
