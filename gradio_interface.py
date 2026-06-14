import gradio as gr
import json
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# 🎤 Định nghĩa giọng đọc theo ngôn ngữ
VOICES_BY_LANGUAGE = {
    'Vietnamese': {
        'Nam': 'vi-VN-NhanNeural',
        'Nữ': 'vi-VN-HoaiMyNeural',
    },
    'English': {
        'Female (US)': 'en-US-AriaNeural',
        'Male (US)': 'en-US-GuyNeural',
        'Female (UK)': 'en-GB-SoniaNeural',
        'Male (UK)': 'en-GB-RyanNeural',
    },
    'Chinese': {
        'Female': 'zh-CN-XiaoxuanNeural',
        'Male': 'zh-CN-YunyangNeural',
    },
    'Japanese': {
        'Female': 'ja-JP-NanamiNeural',
        'Male': 'ja-JP-KeitaNeural',
    },
    'Korean': {
        'Female': 'ko-KR-SunHiNeural',
        'Male': 'ko-KR-InJoonNeural',
    },
    'Spanish': {
        'Female': 'es-ES-ElviraNeural',
        'Male': 'es-ES-AlvaroNeural',
    },
    'French': {
        'Female': 'fr-FR-DeniseNeural',
        'Male': 'fr-FR-HenriNeural',
    },
    'German': {
        'Female': 'de-DE-AmalaNeural',
        'Male': 'de-DE-ConradNeural',
    },
}

LANGUAGE_OPTIONS = list(VOICES_BY_LANGUAGE.keys())

def get_voice_options(language: str) -> List[str]:
    """Lấy danh sách giọng đọc theo ngôn ngữ"""
    return list(VOICES_BY_LANGUAGE.get(language, {}).keys())

def get_voice_code(language: str, voice: str) -> str:
    """Lấy mã giọng đọc"""
    return VOICES_BY_LANGUAGE.get(language, {}).get(voice, 'vi-VN-NhanNeural')

def get_language_code(language: str) -> str:
    """Chuyển tên ngôn ngữ sang mã ngôn ngữ"""
    code_map = {
        'Vietnamese': 'vi',
        'English': 'en',
        'Chinese': 'zh',
        'Japanese': 'ja',
        'Korean': 'ko',
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de',
    }
    return code_map.get(language, 'vi')

def create_video_interface(
    urls_text: str,
    language: str,
    voice: str,
    progress=gr.Progress()
) -> Tuple[str, str]:
    """
    Xử lý video generation với progress tracking
    
    Returns:
        (status_text, detailed_results)
    """
    try:
        # Validate input
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        if not urls:
            return ("❌ Lỗi", "❌ Vui lòng nhập ít nhất một URL")
        
        # Lấy mã ngôn ngữ và giọng đọc
        lang_code = get_language_code(language)
        voice_code = get_voice_code(language, voice)
        
        output_dir = '/content/drive/MyDrive/colab-video-generator/videos'
        
        # Xử lý từng URL với progress
        results = []
        completed = 0
        failed = 0
        
        for idx, url in enumerate(urls, 1):
            progress(value=idx / len(urls), desc=f"Đang xử lý {idx}/{len(urls)}")
            logger.info(f"🔄 [{idx}/{len(urls)}] {url}")
            
            try:
                result = process_url(url, language=lang_code, voice=voice_code, output_dir=output_dir)
                results.append(result)
                
                if result['status'] == 'completed':
                    completed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"❌ Error processing {url}: {e}")
                failed += 1
                results.append({
                    'url': url,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Tạo status text
        status_text = f"""✅ XỬ LÝ HOÀN THÀNH!

📊 Tóm tắt:
• Tổng URL: {len(urls)}
• ✅ Thành công: {completed}
• ❌ Thất bại: {failed}
• 📁 Lưu tại: {output_dir}
"""
        
        # Tạo chi tiết kết quả
        detailed_results = "## 📋 Chi Tiết Kết Quả\n\n"
        
        for result in results:
            if result['status'] == 'completed':
                detailed_results += f"""### ✅ {result['url']}
- **Video**: {result.get('output_video', 'N/A')}
- **Metadata**: {result.get('metadata', 'N/A')}
- **Scenes**: {result.get('steps', {}).get('summary', {}).get('scenes', [])}

"""
            else:
                detailed_results += f"""### ❌ {result['url']}
- **Error**: {result.get('error', 'Unknown error')}

"""
        
        return (status_text, detailed_results)
    
    except Exception as e:
        error_msg = f"❌ Lỗi: {str(e)}"
        logger.error(error_msg)
        return ("❌ Lỗi", error_msg)

def on_language_change(language: str) -> Dict:
    """Cập nhật voice options khi thay đổi ngôn ngữ"""
    voices = get_voice_options(language)
    default_voice = voices[0] if voices else 'Nam'
    
    return gr.update(
        choices=voices,
        value=default_voice
    )

# ===== GRADIO UI =====
with gr.Blocks(
    title="🎬 Colab Video Generator",
    theme=gr.themes.Soft(),
    css="""
    .title-text { text-align: center; font-size: 2.5em; font-weight: bold; }
    .subtitle-text { text-align: center; color: #666; }
    .status-success { color: #10a981; font-weight: bold; }
    .status-error { color: #ef4444; font-weight: bold; }
    """
) as demo:
    
    # Header
    gr.Markdown("# 🎬 AI-Powered Content to Video Generator")
    gr.Markdown("### Chuyển đổi bài viết thành video chuyên nghiệp với AI, TTS & Lip Sync")
    gr.Markdown("---")
    
    with gr.Row():
        # === Cột Input (Trái) ===
        with gr.Column(scale=1):
            gr.Markdown("## ⚙️ Cấu Hình")
            
            urls_input = gr.Textbox(
                label="📝 Danh Sách URL",
                placeholder="https://example.com/article\nhttps://another.com/article\n...",
                lines=8,
                max_lines=20,
                info="Mỗi URL trên một dòng"
            )
            
            with gr.Row():
                language_select = gr.Dropdown(
                    choices=LANGUAGE_OPTIONS,
                    value="Vietnamese",
                    label="🌐 Ngôn Ngữ",
                    interactive=True
                )
            
            voice_select = gr.Dropdown(
                choices=get_voice_options("Vietnamese"),
                value="Nam",
                label="🎤 Giọng Đọc",
                interactive=True,
                info="Chọn giọng đọc theo ngôn ngữ"
            )
            
            # Cập nhật voice khi thay đổi language
            language_select.change(
                fn=on_language_change,
                inputs=language_select,
                outputs=voice_select
            )
            
            with gr.Row():
                submit_btn = gr.Button(
                    "🚀 Tạo Video",
                    variant="primary",
                    size="lg",
                    scale=2
                )
                cancel_btn = gr.Button(
                    "🛑 Dừng",
                    variant="stop",
                    scale=1
                )
            
            gr.Markdown("---")
            gr.Markdown("""
            ### 📚 Hướng Dẫn Nhanh
            1. Nhập URL bài viết (mỗi URL 1 dòng)
            2. Chọn ngôn ngữ
            3. Chọn giọng đọc
            4. Bấm "Tạo Video"
            5. Video sẽ được lưu vào Google Drive
            
            ⏱️ **Thời gian**: ~7-18 phút/URL
            """)
        
        # === Cột Output (Phải) ===
        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.TabItem("📊 Tóm Tắt"):
                    status_output = gr.Textbox(
                        label="Status",
                        interactive=False,
                        lines=12,
                        max_lines=15
                    )
                
                with gr.TabItem("📋 Chi Tiết"):
                    details_output = gr.Markdown(
                        "Chưa có dữ liệu. Bấm 'Tạo Video' để bắt đầu."
                    )
                
                with gr.TabItem("⚙️ Cấu Hình Nâng Cao"):
                    gr.Markdown("""
                    ### Tùy chọn Nâng Cao
                    
                    | Tùy chọn | Mô tả |
                    |---------|-------|
                    | **Số Scenes** | 3-5 scenes mặc định |
                    | **Chất lượng Video** | 1280x720 @ 24fps |
                    | **Format Video** | MP4 (H.264) |
                    | **TTS Engine** | Edge-TTS (Azure Cognitive) |
                    | **Subtitle** | Tự động sinh từ script |
                    
                    **Checkpoint Recovery**: Tự động lưu checkpoint mỗi URL
                    """)
    
    # Click handler
    submit_btn.click(
        fn=create_video_interface,
        inputs=[urls_input, language_select, voice_select],
        outputs=[status_output, details_output],
        api_name="generate"
    )
    
    # Cancel handler (placeholder - cần integrate với process function)
    cancel_btn.click(
        fn=lambda: ("❌ Đã hủy", "Quá trình đã bị dừng lại"),
        outputs=[status_output, details_output]
    )

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 GRADIO SERVER ĐANG KHỞI ĐỘNG...")
    print("="*70 + "\n")
    
    demo.launch(
        share=True,
        debug=False,
        show_error=True,
        server_name="0.0.0.0",
        server_port=7860
    )
