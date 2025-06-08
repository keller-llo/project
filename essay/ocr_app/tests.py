# ocr_app/tests.py

import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'clothing_project.test_settings'
django.setup()


from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
