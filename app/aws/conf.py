import datetime

AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = True

AWS_STORAGE_BUCKET_NAME = "pdf-analyser-stage"

DEFAULT_FILE_STORAGE = "app.aws.utils.MediaRootS3BotoStorage"
STATICFILES_STORAGE = "app.aws.utils.StaticRootS3BotoStorage"
S3DIRECT_REGION = "ap-south-1"
S3_URL = "//%s.s3.amazonaws.com/" % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = "//%s.s3.amazonaws.com/media/" % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + "static/"
ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_REGION_NAME = "ap-south-1"

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = {
    "Expires": expires,
    "Cache-Control": "max-age=%d" % (int(two_months.total_seconds()),),
}
