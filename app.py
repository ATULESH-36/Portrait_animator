import hashlib
import os
import time
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

from src.pipeline import PortraitPipeline

try:
    from streamlit_image_comparison import image_comparison
except Exception:  # pragma: no cover - fallback when package is unavailable
    image_comparison = None


st.set_page_config(
    page_title="Portrait Cartoonifier",
    page_icon="🎨",
    layout="wide",
)


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
        }
        .stApp {
            background: linear-gradient(135deg, #07111f 0%, #111827 100%);
        }
        .hero-title {
            text-align: center;
            font-size: 2.4rem;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 0.2rem;
        }
        .hero-subtitle {
            text-align: center;
            font-size: 1rem;
            color: #cbd5e1;
            margin-bottom: 1.2rem;
        }
        .card {
            background: rgba(15, 23, 42, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 18px;
            padding: 1rem 1.2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22);
            backdrop-filter: blur(10px);
        }
        .info-card {
            background: rgba(30, 41, 59, 0.9);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            border: 1px solid rgba(148, 163, 184, 0.22);
            margin-top: 0.8rem;
        }
        .stImage > img {
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
        }
        .stButton > button {
            border-radius: 999px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        div[data-testid="stSelectbox"] div[role="button"],
        div[data-testid="stSelectbox"] [data-baseweb="select"] {
            cursor: pointer !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def convert_to_rgb(image: np.ndarray) -> np.ndarray:
    if image is None:
        return None
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def load_image(uploaded_file) -> np.ndarray:
    if uploaded_file is None:
        return None

    file_bytes = np.asarray(bytearray(uploaded_file.getvalue()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("The uploaded file could not be read as a valid image.")
    return image





def get_file_hash(uploaded_file) -> str | None:
    if uploaded_file is None:
        return None
    return hashlib.sha256(uploaded_file.getvalue()).hexdigest()


def render_stage_grid(result: dict) -> None:
    stages = [
        ("Preprocessed Image", result["preprocessed"]),
        ("Quantized Image", result["quantized"]),
        ("Edge Map", result["edges"]),
        ("Cartoon Before Post Processing", result["cartoon"]),
    ]

    cols = st.columns(2)
    for idx, (title, image) in enumerate(stages):
        with cols[idx % 2]:
            display_image = convert_to_rgb(image) if len(image.shape) == 3 else image
            st.image(display_image, caption=title, use_container_width=True)


def get_download_targets() -> dict[str, tuple[str, str]]:
    return {
        "Final Cartoon": ("final", "portrait_cartoon.png"),
        "Quantized Image": ("quantized", "portrait_quantized.png"),
        "Original Image": ("original", "portrait_original.png"),
        "Preprocessed Image": ("preprocessed", "portrait_preprocessed.png"),
        "Edge Map": ("edges", "portrait_edges.png"),
        "Cartoon Before Post Processing": ("cartoon", "portrait_cartoon_stage.png"),
    }


def main() -> None:
    inject_custom_css()

    st.markdown('<div class="hero-title">🎨 Portrait Cartoonifier</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Transform your portrait photos into artistic cartoons using Computer Vision and OpenCV.</div>',
        unsafe_allow_html=True,
    )

    if "pipeline" not in st.session_state:
        st.session_state.pipeline = PortraitPipeline()
    if "processed_result" not in st.session_state:
        st.session_state.processed_result = None
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    if "final_cartoon" not in st.session_state:
        st.session_state.final_cartoon = None
    if "processing_time" not in st.session_state:
        st.session_state.processing_time = None
    if "uploaded_file_hash" not in st.session_state:
        st.session_state.uploaded_file_hash = None
    if "result" not in st.session_state:
        st.session_state.result = None
    if "download_choice" not in st.session_state:
        st.session_state.download_choice = "Final Cartoon"

    uploaded_file = None

    with st.sidebar:
        st.markdown("### About")
        st.markdown("**Portrait Cartoonifier**")
        st.markdown("Built using:")
        st.markdown("• OpenCV\n• NumPy\n• Computer Vision\n• Image Processing\n• Streamlit")

        st.markdown("---")
        st.markdown("### Upload Section")
        uploaded_file = st.file_uploader(
            "Upload Portrait Image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload a clear portrait for the best cartoon effect.",
        )

        if uploaded_file is not None:
            current_hash = get_file_hash(uploaded_file)
            previous_hash = st.session_state.get("uploaded_file_hash")
            if previous_hash != current_hash:
                st.session_state.processed_result = None
                st.session_state.uploaded_image = None
                st.session_state.final_cartoon = None
                st.session_state.processing_time = None
                st.session_state.result = None
                st.session_state.download_choice = "Final Cartoon"
                st.session_state.uploaded_file_hash = current_hash
            st.caption(f"Loaded: {uploaded_file.name}")

        st.markdown("---")
        st.markdown("### Processing Information")
        st.write("- Supported Formats: JPG, JPEG, PNG, WEBP")
        st.write("- Recommended Resolution: 800px+ for best detail")
        st.write("- Processing Time: Usually a few seconds")

        generate_button = st.button("Generate Cartoon", type="primary", use_container_width=True)

    if uploaded_file is None:
        st.warning("Please upload a portrait image to begin.")
        st.stop()

    if generate_button:
        try:
            with st.spinner("Creating your cartoon..."):
                start_time = time.time()
                image = load_image(uploaded_file)
                if image is None:
                    raise ValueError("The uploaded file could not be decoded into an image.")

                result = st.session_state.pipeline.cartoonify(image)
                if result is None:
                    raise RuntimeError("The pipeline failed to produce a cartoon image.")

                st.session_state.uploaded_image = image
                st.session_state.processed_result = result
                st.session_state.result = result
                st.session_state.final_cartoon = result["final"]
                st.session_state.processing_time = round(time.time() - start_time, 2)
                st.session_state.download_choice = "Final Cartoon"
                

            st.success("Cartoon generated successfully!")
        except Exception as exc:
            st.error(f"Processing failed: {exc}")
            st.session_state.processed_result = None
            st.session_state.final_cartoon = None
            st.session_state.processing_time = None

    with st.sidebar:
        st.markdown("---")
        st.markdown("### Download Section")
        if st.session_state.processed_result is not None:
            download_targets = get_download_targets()
            selected_download = st.selectbox(
                "Choose image to download",
                options=list(download_targets.keys()),
                index=list(download_targets.keys()).index(st.session_state.download_choice)
                if st.session_state.download_choice in download_targets
                else 0,
                key="download_choice",
            )
            stage_key, file_name = download_targets[selected_download]
            image_to_download = st.session_state.processed_result[stage_key]
            _, buffer = cv2.imencode(".png", image_to_download)
            st.download_button(
                label=f"Download {selected_download}",
                data=buffer.tobytes(),
                file_name=file_name,
                mime="image/png",
            )
        else:
            st.info("Generate a cartoon to enable download.")

    if st.session_state.processed_result is None:
        st.info("Click the button in the sidebar to generate a cartoon from your portrait.")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(convert_to_rgb(st.session_state.uploaded_image), caption="Original Image", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(convert_to_rgb(st.session_state.processed_result["final"]), caption="Final Cartoon Image", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Processing Stages")
    with st.expander("View Processing Stages", expanded=False):
        render_stage_grid(st.session_state.processed_result)

    st.markdown("---")
    st.subheader("Before & After Comparison")
    if image_comparison is not None:
        image_comparison(
            img1=convert_to_rgb(st.session_state.processed_result["original"]),
            img2=convert_to_rgb(st.session_state.processed_result["final"]),
            label1="Original",
            label2="Final Cartoon",
            starting_position=50,
        )
    else:
        st.info("The image comparison component is not available in this environment. The processed images are still shown above.")

    st.markdown("---")
    st.subheader("Quick Info")
    height, width = st.session_state.processed_result["final"].shape[:2]
    st.markdown(
        f"""
        <div class="info-card">
            <strong>Image Resolution:</strong> {width} × {height}<br>
            <strong>Processing Time:</strong> {st.session_state.processing_time} seconds
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
