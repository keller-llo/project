# Clothing Analysis System

A Django-based clothing analysis system that can recognize text information from clothing images and provide intelligent recommendations.

## Features

- Clothing Image Text Recognition (OCR)
- Support for Chinese and Japanese text recognition
- Intelligent clothing recommendations
- Weather-based outfit suggestions
- Image classification and management
- User-friendly web interface

## Tech Stack

- Python 3.x
- Django
- PaddleOCR
- OpenCV
- scikit-learn
- Bootstrap

## Installation

1. Clone the repository:
```bash
git clone https://github.com/keller-llo/project.git
cd project
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run database migrations:
```bash
cd essay
python manage.py migrate
```

5. Start development server:
```bash
python manage.py runserver
```

## Usage

1. Visit http://localhost:8000 to open the application
2. Upload clothing images
3. The system will automatically recognize text information in the images
4. View recognition results and recommendations

## Project Structure

```
essay/
├── clothing_project/    # Django project configuration
├── ocr_app/            # Main application
│   ├── services/       # Business logic services
│   ├── templates/      # HTML templates
│   └── static/         # Static files
├── media/              # Uploaded media files
└── static/             # Static resources
```

## Contributing

Issues and Pull Requests are welcome to help improve the project.

## License

MIT License 