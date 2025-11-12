"""
Simple authentication for the dashboard
"""
import streamlit as st
import hashlib
import os

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password() -> bool:
    """Returns True if the user has entered the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Get password from environment variable or use default
        correct_password = os.getenv("DASHBOARD_PASSWORD", "admin123")
        hashed_correct = hash_password(correct_password)
        hashed_entered = hash_password(st.session_state["password"])

        if hashed_entered == hashed_correct:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    # Return True if password is already validated
    if st.session_state.get("password_correct", False):
        return True

    # Show login form
    st.markdown("""
        <div style="max-width: 400px; margin: 100px auto; padding: 40px;
                    background: white; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h1 style="text-align: center; color: #1a237e; margin-bottom: 30px;">
                🔒 Dashboard Login
            </h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password",
            placeholder="Enter password"
        )

        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Incorrect password. Please try again.")

        st.markdown("""
            <div style="text-align: center; margin-top: 30px; color: #666; font-size: 14px;">
                Enter your password to access the dashboard
            </div>
        """, unsafe_allow_html=True)

    return False
