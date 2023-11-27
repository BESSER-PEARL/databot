import streamlit as st
from streamlit.components.v1 import html


def clear_box(key: str):
    """
    Clears an input box after introducing a value. This is necessary because Streamlit does not clear input boxes after
    introducing a value.

    Args:
        key (str): the key of the streamlit session_state variable containing the input value
    """
    st.session_state[f'{key}_input'] = st.session_state[key]
    st.session_state[key] = ''


def get_input_value(key):
    """
    Gets the value of an input box. This is necessary because Streamlit does not clear input boxes after introducing a
    value. We do it using the clear_box function, storing the value in a temporary variable, and getting it with this
    function.

    Args:
        key (str): the key of the streamlit session_state variable containing the input value
    """
    if f'{key}_input' in st.session_state:
        input_value = st.session_state[f'{key}_input']
        st.session_state[f'{key}_input'] = None
        return input_value
    return None


def disable_input_focusout():
    """Add a script to the UI html code to avoid introducing a value in a text input box when it is focused out, so it
    is only introduced when the enter key is pressed."""
    html(
        """
        <script>
        const doc = window.parent.document;
        const inputs = doc.querySelectorAll('input');
    
        inputs.forEach(input => {
            input.addEventListener('focusout', function(event) {
                event.stopPropagation();
                event.preventDefault();
            });
        });
    
        </script>
        """,
        height=0,
        width=0,
        )
