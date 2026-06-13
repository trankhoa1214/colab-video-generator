"""
Wav2Lip Processor - Lip Sync Module
Xử lý khớp môi (lip sync) cho video
"""

import os
import subprocess
import cv2
import numpy as np
import torch
import dlib
from pathlib import Path
import logging
from typing import Tuple, List
import gdown

logger = logging.getLogger(__name__)

class Wav2LipProcessor:
    """
    Xử lý Lip Sync bằng Wav2Lip
    """
    
    def __init__(self, model_path: str = None, device: str = 'cuda'):
        self.device = device
        self.model_path = model_path or '/tmp/wav2lip_gan.pth'
        self.checkpoint_url = 'https://github.com/Rudrabha/Wav2Lip/releases/download/v1/wav2lip_gan.pth'
        
        # Tải model nếu chưa có
        self._setup_model()
    
    def _setup_model(self):
        """
        Tải Wav2Lip checkpoint
        """
        try:
            if not os.path.exists(self.model_path):
                logger.info(f"📥 Tải Wav2Lip model từ {self.checkpoint_url}...")
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                
                # Download từ GitHub releases
                subprocess.run([
                    'wget', '-q', self.checkpoint_url, '-O', self.model_path
                ], check=True)
                
                logger.info(f"✅ Model tải thành công: {self.model_path}")
            else:
                logger.info(f"✅ Model tồn tại: {self.model_path}")
        except Exception as e:
            logger.error(f"❌ Lỗi tải model: {e}")
    
    def _import_wav2lip_models(self):
        """
        Import Wav2Lip models từ GitHub
        """
        try:
            # Clone Wav2Lip repo
            wav2lip_dir = '/tmp/Wav2Lip'
            if not os.path.exists(wav2lip_dir):
                logger.info("📥 Clone Wav2Lip repository...")
                subprocess.run([
                    'git', 'clone', 
                    'https://github.com/Rudrabha/Wav2Lip.git',
                    wav2lip_dir
                ], capture_output=True, check=False)
            
            return wav2lip_dir
        except Exception as e:
            logger.error(f"❌ Lỗi import Wav2Lip: {e}")
            return None
    
    def extract_face(self, video_path: str, output_dir: str = None) -> Tuple[List[str], List[dict]]:
        """
        Trích xuất khuôn mặt từ video
        """
        try:
            if not output_dir:
                output_dir = '/tmp/faces'
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"🔍 Trích xuất khuôn mặt từ video...")
            
            # Khởi tạo dlib face detector
            detector = dlib.get_frontal_face_detector()
            
            # Mở video
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            faces_frames = []
            face_rects = []
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Phát hiện khuôn mặt
                dets = detector(gray, 1)
                
                if len(dets) > 0:
                    # Lấy khuôn mặt lớn nhất
                    det = max(dets, key=lambda x: (x.right() - x.left()) * (x.bottom() - x.top()))
                    
                    x1 = max(0, det.left() - 20)
                    y1 = max(0, det.top() - 20)
                    x2 = min(frame.shape[1], det.right() + 20)
                    y2 = min(frame.shape[0], det.bottom() + 20)
                    
                    face_crop = frame[y1:y2, x1:x2]
                    
                    # Lưu ảnh khuôn mặt
                    face_path = f'{output_dir}/face_{frame_count:05d}.jpg'
                    cv2.imwrite(face_path, face_crop)
                    
                    faces_frames.append(face_path)
                    face_rects.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'frame': frame_count})
            
            cap.release()
            
            logger.info(f"✅ Trích xuất {len(faces_frames)} frame có khuôn mặt")
            return faces_frames, face_rects
        
        except Exception as e:
            logger.error(f"❌ Lỗi trích xuất khuôn mặt: {e}")
            return [], []
    
    def generate_lip_sync_video(self, video_path: str, audio_path: str, output_path: str = None) -> str:
        """
        Tạo video với lip sync bằng Wav2Lip
        
        Phương pháp: Sử dụng Wav2Lip inference từ CLI
        """
        try:
            if not output_path:
                output_path = video_path.replace('.mp4', '_lipsync.mp4')
            
            logger.info(f"🎤 Tạo Lip Sync video...")
            logger.info(f"  Video input: {video_path}")
            logger.info(f"  Audio input: {audio_path}")
            
            wav2lip_dir = self._import_wav2lip_models()
            if not wav2lip_dir:
                logger.warning("⚠️ Không thể tải Wav2Lip repo, bỏ qua lip sync")
                return video_path
            
            # Chạy Wav2Lip inference
            cmd = [
                'python', f'{wav2lip_dir}/inference.py',
                '--checkpoint_path', self.model_path,
                '--face', video_path,
                '--audio', audio_path,
                '--outfile', output_path
            ]
            
            logger.info(f"🔄 Chạy Wav2Lip inference (có thể mất 5-15 phút)...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0 and os.path.exists(output_path):\n                logger.info(f\"✅ Lip sync video tạo thành công: {output_path}\")\n                return output_path\n            else:\n                logger.warning(f\"⚠️ Wav2Lip inference thất bại: {result.stderr}\")\n                # Trả về video gốc nếu lip sync thất bại\n                return video_path\n        \n        except subprocess.TimeoutExpired:\n            logger.warning(\"⚠️ Wav2Lip timeout (>30 phút), bỏ qua lip sync\")\n            return video_path\n        except Exception as e:\n            logger.error(f\"❌ Lỗi Wav2Lip: {e}\")\n            return video_path\n    \n    def process_video_with_lipsync(self, video_path: str, audio_path: str, output_path: str = None) -> str:\n        \"\"\"\n        Pipeline xử lý video với lip sync\n        \"\"\"\n        try:\n            if not output_path:\n                output_path = video_path.replace('.mp4', '_with_lipsync.mp4')\n            \n            logger.info(f\"\\n{'='*60}\")\n            logger.info(f\"📹 PROCESSING VIDEO WITH LIP SYNC\")\n            logger.info(f\"{'='*60}\")\n            \n            # Bước 1: Trích xuất khuôn mặt\n            faces, rects = self.extract_face(video_path)\n            \n            if not faces:\n                logger.warning(\"⚠️ Không tìm thấy khuôn mặt trong video\")\n                return video_path\n            \n            # Bước 2: Tạo lip sync\n            result = self.generate_lip_sync_video(video_path, audio_path, output_path)\n            \n            # Giải phóng GPU\n            if torch.cuda.is_available():\n                torch.cuda.empty_cache()\n            \n            return result\n        \n        except Exception as e:\n            logger.error(f\"❌ Lỗi xử lý lip sync: {e}\")\n            return video_path\n\n\ndef apply_wav2lip_to_video(video_path: str, audio_path: str, output_path: str = None, device: str = 'cuda') -> str:\n    \"\"\"\n    Wrapper function để dễ sử dụng\n    \"\"\"\n    processor = Wav2LipProcessor(device=device)\n    return processor.process_video_with_lipsync(video_path, audio_path, output_path)\n
