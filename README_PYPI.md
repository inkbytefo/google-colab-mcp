# 🚀 PyPI Yayınlama Rehberi

Bu rehber, MCP Colab Server paketini PyPI'ye yayınlama sürecini açıklar.

## 📋 Ön Gereksinimler

1. **PyPI Hesabı**: [PyPI](https://pypi.org) ve [Test PyPI](https://test.pypi.org) hesapları
2. **API Token**: PyPI hesabınızdan API token oluşturun
3. **Gerekli Paketler**: 
   ```bash
   pip install build twine
   ```

## 🔧 Kurulum

### 1. Paket Yapısını Kontrol Edin

```
google-colab-mcp/
├── src/
│   └── mcp_colab_server/
│       ├── __init__.py
│       ├── server.py
│       ├── auth_manager.py
│       └── ...
├── pyproject.toml
├── README.md
├── LICENSE
└── build_and_publish.py
```

### 2. Version Güncelleme

`src/mcp_colab_server/__init__.py` dosyasında version'ı güncelleyin:
```python
__version__ = "1.0.1"  # Yeni version
```

`pyproject.toml` dosyasında da version'ı güncelleyin:
```toml
[project]
version = "1.0.1"
```

## 🏗️ Build ve Test

### 1. Test PyPI'ye Yükleme

```bash
# Build ve Test PyPI'ye yükle
python build_and_publish.py --test
```

### 2. Test Kurulumu

```bash
# Test PyPI'den kur
pip install --index-url https://test.pypi.org/simple/ google-colab-mcp

# Test et
google-colab-mcp-setup --help
google-colab-mcp --help
```

### 3. Production PyPI'ye Yükleme

```bash
# Production PyPI'ye yükle
python build_and_publish.py --prod
```

## 🔐 API Token Kurulumu

### 1. PyPI Token Oluşturma

1. [PyPI Account Settings](https://pypi.org/manage/account/) → API tokens
2. "Add API token" → Scope: "Entire account" veya specific project
3. Token'ı kopyalayın

### 2. Token'ı Kaydetme

```bash
# ~/.pypirc dosyası oluşturun
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

## 📦 Manuel Build Süreci

### 1. Temizlik

```bash
rm -rf build/ dist/ *.egg-info/
```

### 2. Build

```bash
python -m build
```

### 3. Upload

```bash
# Test PyPI
python -m twine upload --repository testpypi dist/*

# Production PyPI
python -m twine upload dist/*
```

## ✅ Doğrulama

### 1. Paket Sayfası

- Test: https://test.pypi.org/project/google-colab-mcp/
- Production: https://pypi.org/project/google-colab-mcp/

### 2. Kurulum Testi

```bash
# Yeni virtual environment
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# Paketi kur
pip install google-colab-mcp

# Test et
google-colab-mcp --version
google-colab-mcp-setup --help
```

## 🚨 Sorun Giderme

### Build Hataları

```bash
# Dependencies kontrol et
pip install --upgrade build twine setuptools wheel

# Syntax kontrol et
python -m py_compile src/mcp_colab_server/*.py
```

### Upload Hataları

```bash
# Token kontrol et
cat ~/.pypirc

# Network kontrol et
python -m twine check dist/*
```

### Import Hataları

```bash
# Package structure kontrol et
python -c "import mcp_colab_server; print(mcp_colab_server.__version__)"
```

## 📈 Version Management

### Semantic Versioning

- **Major** (1.0.0 → 2.0.0): Breaking changes
- **Minor** (1.0.0 → 1.1.0): New features, backward compatible
- **Patch** (1.0.0 → 1.0.1): Bug fixes

### Release Checklist

- [ ] Version güncellendi
- [ ] CHANGELOG.md güncellendi
- [ ] Tests geçiyor
- [ ] Documentation güncel
- [ ] Test PyPI'de test edildi
- [ ] Production PyPI'ye yüklendi
- [ ] GitHub release oluşturuldu
- [ ] Social media duyurusu yapıldı

## 🎉 İlk Release Sonrası

1. **GitHub Release**: Tag oluşturun ve release notes yazın
2. **Documentation**: PyPI linklerini güncelleyin
3. **Community**: Reddit, Twitter, Discord'da duyurun
4. **Feedback**: Issue tracker'ı takip edin

---

**Başarılar! 🚀 Paketiniz artık dünya çapında kullanılabilir!**