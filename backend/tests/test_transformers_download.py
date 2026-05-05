import os
import hashlib
import pytest
import requests_mock
from django.conf import settings
from apps.nasa_ingest.transformers.apod import APODTransformer
from apps.nasa_ingest.transformers.mars import MarsPhotoTransformer
from apps.nasa_ingest.transformers.epic import EPICTransformer

@pytest.mark.django_db
def test_apod_transformer_download():
    url = "https://example.com/apod.jpg"
    raw = {
        "date": "2026-04-13", "title": "T", "explanation": "E",
        "media_type": "image", "url": url, "hdurl": "",
    }
    
    with requests_mock.Mocker() as m:
        m.get(url, content=b"fake image data")
        
        transformer = APODTransformer(raw)
        entry = transformer.to_model()
        
        # Verify proxied_url is set and points to media
        assert entry.proxied_url.startswith(settings.MEDIA_URL)
        
        # Verify file exists on disk
        relative_path = entry.proxied_url.replace(settings.MEDIA_URL, "")
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        assert os.path.exists(full_path)
        with open(full_path, "rb") as f:
            assert f.read() == b"fake image data"

@pytest.mark.django_db
def test_mars_photo_transformer_download():
    url = "https://example.com/mars.jpg"
    raw = [
        {"id": 1, "sol": 100, "earth_date": "2026-04-01", "img_src": url,
         "rover": {"name": "Perseverance"}, "camera": {"short_name": "NAVCAM"}}
    ]
    
    with requests_mock.Mocker() as m:
        m.get(url, content=b"mars data")
        
        transformer = MarsPhotoTransformer(raw)
        photos = transformer.to_models()
        
        assert len(photos) == 1
        assert photos[0].proxied_url.startswith(settings.MEDIA_URL)
        
        full_path = os.path.join(settings.MEDIA_ROOT, photos[0].proxied_url.replace(settings.MEDIA_URL, ""))
        assert os.path.exists(full_path)

@pytest.mark.django_db
def test_epic_transformer_download():
    # EPICTransformer needs a client that provides the URL
    raw = [{
        "identifier": "20260401", "image": "epic_1", "date": "2026-04-01 12:00:00",
        "caption": "Earth", "centroid_coordinates": {"lat": 0, "lon": 0}
    }]
    
    with requests_mock.Mocker() as m:
        # Mock the image URL that the client would generate
        # In the real code, EPICClient.image_url() is used.
        # We need to know what it produces or mock the client too.
        # Let's mock the internal call to _proxy_image by providing a fixed URL in the client mock if possible,
        # but easier to just let it run and mock the resulting URL.
        
        from apps.nasa_ingest.clients.epic import EPICClient
        client = EPICClient()
        url = client.image_url("epic_1", "2026-04-01")
        
        m.get(url, content=b"epic data")
        
        transformer = EPICTransformer(raw)
        images = transformer.to_models()
        
        assert len(images) == 1
        assert images[0].proxied_url.startswith(settings.MEDIA_URL)
        
        full_path = os.path.join(settings.MEDIA_ROOT, images[0].proxied_url.replace(settings.MEDIA_URL, ""))
        assert os.path.exists(full_path)

@pytest.mark.django_db
def test_transformer_download_failure():
    url = "https://example.com/fail.jpg"
    raw = {
        "date": "2026-04-14", "title": "F", "explanation": "E",
        "media_type": "image", "url": url,
    }
    
    with requests_mock.Mocker() as m:
        m.get(url, status_code=404)
        
        transformer = APODTransformer(raw)
        entry = transformer.to_model()
        
        # Should fallback to raw URL if download fails
        assert entry.proxied_url == url
