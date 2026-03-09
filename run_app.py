import sys
import asyncio

# Python 3.14 removed the automatic creation of event loops in get_event_loop()
# Streamlit relies on this old behavior. We monkey-patch it here.

original_get_event_loop = asyncio.get_event_loop

def patched_get_event_loop():
    try:
        return original_get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

asyncio.get_event_loop = patched_get_event_loop

# Now we can safely import and run Streamlit
import streamlit.web.cli as stcli

if __name__ == "__main__":
    # Simulate 'streamlit run app.py'
    sys.argv = ["streamlit", "run", "app.py"]
    sys.exit(stcli.main())
