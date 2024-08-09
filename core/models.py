from django.db import models
from app.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

import boto3
import tempfile
from io import BytesIO
import fitz
import re

USE_S3 = settings.USE_S3


def upload_to(instance, filename):
    return "documents/{0}/{1}".format(instance.id, filename)


class ReviewRequest(BaseModel):
    status = models.CharField(max_length=100, default="pending")
    reviewer = models.ForeignKey("users.User", on_delete=models.CASCADE)
    document = models.FileField(upload_to=upload_to)
    comments = models.TextField()

    class Meta:
        verbose_name = "Review Request"
        verbose_name_plural = "Review Requests"


@receiver(post_save, sender=ReviewRequest)
def review_request_post_save(sender, instance, created, **kwargs):
    if created:
        if USE_S3:
            s3 = boto3.client("s3")
            document = instance.document
            path = f"media/{document.name}"
            document_data = s3.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=path
            )
            document_content = document_data["Body"].read()
            document_stream = BytesIO(document_content)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(document_content)
                tmp_file_path = tmp_file.name

            try:
                fitz_analyzer = FitsAnalyzer(tmp_file_path, instance.id)
                document_stream.close()
            finally:
                tmp_file.close()
                tmp_file.unlink(tmp_file_path)
        else:
            document_path = instance.document.path
            fitz_analyzer = FitsAnalyzer(document_path, instance.id)
            instance.document.close()


class PageResult(BaseModel):
    review_request = models.ForeignKey(ReviewRequest, on_delete=models.CASCADE)
    page_number = models.PositiveIntegerField()
    service = models.CharField(
        max_length=100
    )  # method or service which was used to extract the data
    details = models.JSONField()

    def __str__(self):
        return f"{str(self.review_request.id)} - {self.page_number}"

    class Meta:
        unique_together = ("review_request", "page_number", "service")
        verbose_name = "Page Result"
        verbose_name_plural = "Page Results"


class FitsAnalyzer:
    def __init__(self, pdf_path, review_request):
        self.pdf = fitz.open(pdf_path)
        self.analysis = {}
        self.analyse()
        self.save_results(review_request)

    def save_results(self, review_request_id):
        for page_num, details in self.analysis.items():
            PageResult.objects.create(
                review_request_id=review_request_id,
                page_number=page_num,
                service="fitz",
                details=details,
            )

    def analyse(self):
        num_pages = self.pdf.page_count
        for page_num in range(num_pages):
            page = self.pdf.load_page(page_num)
            self.analysis[page_num] = {
                "margins": self.get_page_margins(page),
                "is_blank": self.is_blank_page(page),
                # 'is_single_side': self.is_single_side_page(page),
                # 'is_double_side': self.is_double_side_page(page),
                "side": "single" if self.is_single_side_page(page) else "double",
                "is_page_numbered": self.is_page_numbered(page),
                "page_number_coordinates": self.page_numbers_and_coordinates(page),
                "is_landscaped": self.is_landscaped(page),
                "is_portraited": self.is_portraited(page),
                "orientation": "landscape" if self.is_landscaped(page) else "portrait",
                "text_percentage": self.get_text_percentage(page),
            }

    def get_page_margins(self, page):
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height

        text_blocks = page.get_text("blocks")

        # Initialize margins
        top_margin = page_height
        bottom_margin = page_height
        left_margin = page_width
        right_margin = page_width

        # Calculate the margins
        for block in text_blocks:
            block_rect = fitz.Rect(block[:4])

            top_margin = min(top_margin, block_rect.y0)
            bottom_margin = min(bottom_margin, page_height - block_rect.y1)
            left_margin = min(left_margin, block_rect.x0)
            right_margin = min(right_margin, page_width - block_rect.x1)

        return {
            "top": top_margin,
            "bottom": bottom_margin,
            "left": left_margin,
            "right": right_margin,
        }

    def is_blank_page(self, page):
        text_blocks = page.get_text("blocks")
        image_list = page.get_images(full=True)

        if not text_blocks and not image_list:
            return True
        return False

    def is_single_side_page(self, page):
        ## it'll be decided based on the left ma
        return 0

    def is_double_side_page(self, page):
        return 0

    def is_page_numbered(self, page):
        text = page.get_text()
        lat_lon_pattern = re.compile(r"([-+]?\d{1,2}\.\d+),\s*([-+]?\d{1,3}\.\d+)")
        matches = lat_lon_pattern.findall(text)
        return bool(matches)

    def page_numbers_and_coordinates(self, page):
        lat_lon_pattern = re.compile(r"([-+]?\d{1,2}\.\d+),\s*([-+]?\d{1,3}\.\d+)")
        text = page.get_text()
        matches = lat_lon_pattern.findall(text)
        return matches

    def is_landscaped(self, page):
        page_rect = page.rect
        return page_rect.width > page_rect.height

    def is_portraited(self, page):
        page_rect = page.rect
        return page_rect.width < page_rect.height

    def get_text_percentage(self, page):
        text = page.get_text()
        page_rect = page.rect
        text_area = 0
        for block in page.get_text("blocks"):
            block_rect = fitz.Rect(block[:4])
            text_area += block_rect.width * block_rect.height

        page_area = page_rect.width * page_rect.height
        return (text_area / page_area) * 100
