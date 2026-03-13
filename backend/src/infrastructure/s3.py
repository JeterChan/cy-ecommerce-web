import boto3
from botocore.config import Config
from typing import Optional
from infrastructure.config import settings
import logging

logger = logging.getLogger(__name__)

class S3Client:
    """AWS S3 客戶端封裝，用於處理圖片上傳與預簽名 URL"""

    def __init__(self):
        self.bucket_name = settings.AWS_S3_BUCKET
        self.region = settings.AWS_S3_REGION
        
        # 僅在配置存在時初始化 boto3
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=self.region,
                config=Config(signature_version="s3v4")
            )
        else:
            self.client = None
            logger.warning("AWS S3 憑證未配置，S3 功能將無法使用")

    def generate_presigned_url(
        self, 
        object_name: str, 
        expiration: int = 3600,
        content_type: str = "image/jpeg"
    ) -> Optional[str]:
        """
        生成上傳用的預簽名 URL (PUT 方法)
        
        Args:
            object_name: S3 中的檔案路徑/名稱
            expiration: 有效時間 (秒)
            content_type: 檔案類型
            
        Returns:
            str: 預簽名 URL，若失敗則回傳 None
        """
        if not self.client:
            return None

        try:
            response = self.client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_name,
                    "ContentType": content_type
                },
                ExpiresIn=expiration
            )
            return response
        except Exception as e:
            logger.error(f"生成 S3 預簽名 URL 失敗: {str(e)}")
            return None

# 全域單例
s3_client = S3Client()
