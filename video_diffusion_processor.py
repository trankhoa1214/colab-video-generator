"""
Video Diffusion Processor - Text-to-Video Generation
Tạo video từ text prompt bằng Stable Video Diffusion
"""

import os
import torch
import numpy as np
from pathlib import Path
import logging
from typing import List, Optional
from diffusers import DiffusionPipeline
import cv2
from PIL import Image
import gc

logger = logging.getLogger(__name__)

class VideoDiffusionProcessor:
    """
    Xử lý tạo video từ prompt bằng Stable Video Diffusion
    """
    
    def __init__(self, model_id: str = "stabilityai/stable-video-diffusion-img2vid-xt", device: str = 'cuda'):
        self.model_id = model_id
        self.device = device
        self.pipeline = None
        self.vram_required_gb = 24  # Yêu cầu VRAM tối thiểu
        
        self._check_vram()
    
    def _check_vram(self):
        """
        Kiểm tra VRAM có đủ không
        """
        try:
            if torch.cuda.is_available():
                vram_available = torch.cuda.get_device_properties(0).total_memory / 1e9
                logger.info(f"📊 VRAM available: {vram_available:.2f} GB")
                logger.info(f"📊 VRAM required: {self.vram_required_gb:.2f} GB")
                
                if vram_available < self.vram_required_gb:
                    logger.warning(f"⚠️ VRAM không đủ cho Stable Video Diffusion!")
                    logger.warning(f"   Khuyến nghị: Sử dụng phương pháp thay thế (image to video)")
        except Exception as e:
            logger.warning(f"⚠️ Không thể kiểm tra VRAM: {e}")
    
    def _load_pipeline(self):
        """
        Tải Stable Video Diffusion pipeline
        """
        try:
            if self.pipeline is None:
                logger.info(f"📥 Tải {self.model_id}...")
                
                # Load pipeline với fp16 để tiết kiệm VRAM
                self.pipeline = DiffusionPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16,
                    variant="fp16"
                )
                
                # Enable memory optimization
                self.pipeline.enable_attention_slicing()
                self.pipeline.to(self.device)
                
                logger.info(f"✅ Pipeline đã tải")
            
            return self.pipeline
        
        except Exception as e:
            logger.error(f"❌ Lỗi tải pipeline: {e}")
            return None
    
    def _free_memory(self):
        """
        Giải phóng bộ nhớ GPU
        """
        try:
            if self.pipeline is not None:
                del self.pipeline
                self.pipeline = None
            
            torch.cuda.empty_cache()
            gc.collect()
            logger.info("✅ Bộ nhớ đã được giải phóng")
        except Exception as e:
            logger.warning(f"⚠️ Lỗi giải phóng bộ nhớ: {e}")
    
    def create_placeholder_image(self, prompt: str, width: int = 1280, height: int = 720) -> Image.Image:
        """
        Tạo ảnh placeholder từ text prompt (khi không có GPU mạnh)
        Phương pháp này tiết kiệm VRAM
        """
        try:
            logger.info(f"🎨 Tạo placeholder image từ prompt: {prompt[:50]}...")
            
            # Tạo ảnh gradient với text
            img = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Gradient màu sắc dựa trên prompt
            hash_value = hash(prompt) % 256
            for i in range(height):
                ratio = i / height
                img[i, :] = [
                    int(100 + 155 * np.sin(ratio + hash_value/256)),
                    int(150 + 105 * np.cos(ratio)),
                    int(200 + 55 * np.sin(ratio + 1))
                ]
            
            # Thêm text
            import cv2
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.2
            color = (255, 255, 255)
            thickness = 2
            
            # Wrap text
            words = prompt.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line) + len(word) > 50:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line += " " + word if current_line else word
            if current_line:
                lines.append(current_line)
            
            # Vẽ text
            y_offset = 150
            for line in lines:
                cv2.putText(img, line, (100, y_offset), font, font_scale, color, thickness)
                y_offset += 80
            
            # Thêm watermark
            cv2.putText(img, "AI-Generated Visual Prompt", (50, height - 50), 
                       font, 0.8, (200, 200, 200), 1)
            
            return Image.fromarray(img)
        
        except Exception as e:
            logger.error(f"❌ Lỗi tạo placeholder: {e}")
            # Tạo ảnh solid màu xanh dương
            return Image.new('RGB', (width, height), color=(25, 50, 100))
    
    def generate_video_from_image(self, image: Image.Image, output_path: str, 
                                 num_frames: int = 25, fps: int = 24) -> str:
        """
        Tạo video từ ảnh bằng Stable Video Diffusion
        """
        try:
            logger.info(f"🎬 Tạo video từ ảnh ({num_frames} frames)...")
            
            pipeline = self._load_pipeline()
            if not pipeline:
                logger.error("❌ Không thể tải pipeline")
                return None
            
            # Resize ảnh
            image = image.resize((1024, 576))
            
            logger.info(f"🔄 Running diffusion pipeline (có thể mất 5-10 phút)...")
            
            # Generate video frames
            frames = pipeline(
                image,
                height=576,
                width=1024,
                num_frames=num_frames,
                num_inference_steps=25,
                guidance_scale=1.2
            ).frames[0]
            
            logger.info(f"✅ Tạo {len(frames)} frames thành công")
            
            # Lưu video từ frames
            from moviepy.editor import ImageSequenceClip
            
            frames_np = [np.array(f) for f in frames]
            video_clip = ImageSequenceClip(frames_np, fps=fps)
            video_clip.write_videofile(output_path, verbose=False, logger=None)
            video_clip.close()
            
            logger.info(f"✅ Video lưu tại: {output_path}")
            
            return output_path
        
        except Exception as e:
            logger.error(f"❌ Lỗi tạo video: {e}")
            return None
        
        finally:
            self._free_memory()
    
    def generate_video_from_prompt(self, prompt: str, output_path: str = None, 
                                  use_placeholder: bool = False) -> str:
        """
        Tạo video từ text prompt
        
        Args:
            prompt: Text mô tả video
            output_path: Đường dẫn lưu video
            use_placeholder: Nếu True, sử dụng placeholder image thay vì diffusion
        """
        try:
            if not output_path:
                output_path = f'/tmp/generated_video_{hash(prompt) % 10000}.mp4'
            
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"📹 VIDEO DIFFUSION GENERATION")
            logger.info(f"{'='*60}")
            logger.info(f"Prompt: {prompt}")
            
            if use_placeholder:
                logger.info("🎨 Sử dụng placeholder image (tiết kiệm VRAM)...")
                image = self.create_placeholder_image(prompt)
            else:
                # Có thể tích hợp text-to-image model ở đây (ví dụ: Stable Diffusion)
                logger.warning("⚠️ Tính năng Text-to-Image chưa được tích hợp")
                logger.info("📌 Sử dụng placeholder image thay thế...")
                image = self.create_placeholder_image(prompt)
            
            # Tạo video từ ảnh
            video_path = self.generate_video_from_image(image, output_path)
            
            return video_path
        
        except Exception as e:
            logger.error(f"❌ Lỗi tạo video từ prompt: {e}")
            return None
    
    def batch_generate_videos(self, prompts: List[str], output_dir: str = None) -> List[str]:
        """
        Tạo nhiều video từ danh sách prompt
        """
        try:
            if not output_dir:
                output_dir = '/tmp/generated_videos'
            os.makedirs(output_dir, exist_ok=True)
            
            video_paths = []
            
            for idx, prompt in enumerate(prompts, 1):
                logger.info(f"\n[{idx}/{len(prompts)}] Xử lý prompt...")
                
                output_path = f'{output_dir}/video_{idx:03d}.mp4'
                video_path = self.generate_video_from_prompt(prompt, output_path, use_placeholder=True)
                
                if video_path:
                    video_paths.append(video_path)
            
            logger.info(f"\n✅ Tạo {len(video_paths)} video thành công")
            return video_paths
        
        except Exception as e:
            logger.error(f"❌ Lỗi batch generation: {e}")
            return []


def generate_video_from_text(prompt: str, output_path: str = None, use_placeholder: bool = True) -> str:
    """
    Wrapper function dễ sử dụng
    """
    processor = VideoDiffusionProcessor()
    return processor.generate_video_from_prompt(prompt, output_path, use_placeholder)


def generate_videos_batch(prompts: List[str], output_dir: str = None) -> List[str]:
    """
    Wrapper function cho batch processing
    """
    processor = VideoDiffusionProcessor()
    return processor.batch_generate_videos(prompts, output_dir)
