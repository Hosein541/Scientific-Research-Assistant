import streamlit as st
import sys 
import os 
from pathlib import Path
import shutil
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OUTPUT_DIR, UPLOADS_DIR, CHROMA_DIR

from pipeline import run_pipeline
from core.session_manager import (
    load_settings,
    save_settings
)


settings = load_settings()

# def reset_session():
#     print("🚀 Starting aggressive reset...")

#     # 1. بستن تمام اتصالات Chroma
#     try:
#         SharedSystemClient._identifier_to_system.clear()
        
#         # Force close all systems
#         for key in list(SharedSystemClient._identifier_to_system.keys()):
#             try:
#                 system = SharedSystemClient._identifier_to_system.pop(key, None)
#                 if system and hasattr(system, 'stop'):
#                     system.stop()
#             except:
#                 pass
#     except:
#         pass

#     gc.collect()
#     time.sleep(0.5)   # کمی صبر برای release lock

#     # 2. حذف فولدرها با روش خیلی قوی‌تر
#     folders = [
#         Path("inputs/papers"),
#         Path("outputs"),
#         Path(CHROMA_DIR) / "chroma_db",        # مسیر اصلی از config
#         Path("vector_db/chroma_db"),
#     ]

#     for folder in folders:
#         if not folder.exists():
#             continue
            
#         print(f"Deleting: {folder}")
#         deleted = False
        
#         # روش 1: shutil
#         try:
#             shutil.rmtree(folder, ignore_errors=True)
#             if not folder.exists():
#                 deleted = True
#         except:
#             pass

#         # روش 2: Force Windows delete
#         if not deleted and folder.exists():
#             print(f"Force deleting with Windows commands: {folder}")
#             try:
#                 # استفاده از cmd برای حذف مقاوم
#                 os.system(f'rmdir /s /q "{folder}" 2>nul')
#                 time.sleep(0.3)
                
#                 # اگر هنوز مونده، فایل به فایل حذف کن
#                 if folder.exists():
#                     for root, dirs, files in os.walk(folder, topdown=False):
#                         for file in files:
#                             try:
#                                 file_path = os.path.join(root, file)
#                                 os.chmod(file_path, 0o777)
#                                 os.remove(file_path)
#                             except:
#                                 pass
#                         for d in dirs:
#                             try:
#                                 os.rmdir(os.path.join(root, d))
#                             except:
#                                 pass
#                     os.rmdir(folder)
#             except Exception as e:
#                 print(f"Force delete failed: {e}")

#     # 3. پاک کردن فایل تنظیمات
#     try:
#         settings_file = Path("session/settings.json")
#         if settings_file.exists():
#             settings_file.unlink(missing_ok=True)
#     except:
#         pass

#     print("✅ Reset completed successfully.")

    
# if st.session_state.get("do_reset"):
#     reset_session()
#     st.session_state["do_reset"] = False
#     st.success("Session restarted.")
#     st.rerun()


model_name = st.selectbox(
    "Model",
    [
        "gemini-3.1-flash-lite",
        "gemini-3-flash-preview",
        "gemini-3-pro",
    ]
)

# language = st.selectbox(
#     "Language",
#     [
#         "English",
#         "Deutch",
#         "Persian",
#         "Latin"
#     ]
# )

language = "English"

google_api_key = st.text_input(
    "Google API Key",
    type="password"
)

hf_token = st.text_input(
    "HF Token",
    type="password"
)

uploaded_files = st.file_uploader(
    "Upload Papers",
    type=["pdf"],
    accept_multiple_files=True
)


if st.button(
    "Start Session"
):
        db_name = datetime.now().strftime(
            "chroma_%Y%m%d_%H%M%S"
        )
        settings = {

        "llm_provider":
            "google",

        "llm_model":
            model_name,

        "embedding_model":
            "embeddinggemma",

        "google_api_key":
            google_api_key,

        "hf_token":
            hf_token,
        
        "language":
            language,
        
        "db_name":
            db_name,

        "is_processed":
            False
    }
        
        save_settings(
            settings
        )
    

        UPLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        for file in uploaded_files:
        
            save_path = (
                UPLOADS_DIR
                / file.name
            )

            with open(
                save_path,
                "wb"
            ) as f:

                f.write(
                    file.getbuffer()
                )
        chroma_dir = Path(CHROMA_DIR)
        if chroma_dir.exists() and chroma_dir.is_dir():
            for item in chroma_dir.iterdir():          # iterate over contents
                if item.is_dir() and item.name != db_name:
                    try:
                        shutil.rmtree(item)
                    except Exception as e:
                        print(f"Failed to remove {item}: {e}")

        run_pipeline(model_name, google_api_key, hf_token, language)

        settings["is_processed"] = True
        st.success("Now your system is ready.")
        save_settings(
            settings
    )

def reset_session():

    folders = [
        Path("inputs/papers"),
        Path("outputs"),
        Path("vector_db/chroma_db"),
    ]

    for folder in folders:
        if folder.exists():
            print(folder)
            try:
                shutil.rmtree(
                    folder
                )
            except:
                pass

    settings_file = Path(
        "session/settings.json"
    )

    if settings_file.exists():

        settings_file.unlink()   


# if st.button("Restart Session"):
#     st.session_state["confirm_restart"] = True

# if st.session_state.get("confirm_restart"):

#     st.warning(
#         "This will delete all current session data."
#     )

#     col1, col2 = st.columns(2)

#     with col1:

#         if st.button("Yes, Delete Everything"):

#             reset_session()

#             st.session_state["confirm_restart"] = False

#             st.success(
#                 "Session restarted."
#             )

#             st.rerun()

#     with col2:

#         if st.button("Cancel"):

#             st.session_state["confirm_restart"] = False

#             st.rerun()



if st.button("Restart Session"):
    st.session_state["confirm_restart"] = True

if st.session_state.get("confirm_restart"):

    st.warning(
        "This will delete all current session data."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Yes, Delete Everything"):

            reset_session()

            st.session_state["confirm_restart"] = False

            st.success(
                "Session restarted."
            )

            st.rerun()

    with col2:

        if st.button("Cancel"):

            st.session_state["confirm_restart"] = False

            st.rerun()
# دکمه ریستارت
# if st.button("Restart Session"):
#     st.session_state["confirm_restart"] = True

# if st.session_state.get("confirm_restart"):
#     st.warning("This will delete all current session data.")
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Yes, Delete Everything"):
#             # به جای حذف فوری، پرچم می‌گذاریم و ریلود می‌کنیم
#             st.session_state["do_reset"] = True
#             st.session_state["confirm_restart"] = False
#             st.rerun()
#     with col2:
#         if st.button("Cancel"):
#             st.session_state["confirm_restart"] = False
#             st.rerun()