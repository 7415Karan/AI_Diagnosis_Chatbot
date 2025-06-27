# AI Diagnosis Document Analyzer

This project is a Flask-based web application that serves as a backend for an AI-powered document analysis tool. It accepts uploaded documents (such as PDFs, DOCX files, and images), extracts the text content, and uses the Groq API with LangChain to provide an AI-generated diagnosis or summary.

## Features

- **File Uploads**: Securely handles uploads for various document formats.
- **Multi-Format Text Extraction**:
  - Extracts text from PDF files using `PyMuPDF`.
  - Extracts text from Microsoft Word documents (`.docx`) using `python-docx`.
  - Performs Optical Character Recognition (OCR) on images using `pytesseract` and `Pillow`.
- **AI-Powered Analysis**: Leverages the speed of the Groq LPU™ Inference Engine via `langchain-groq` for fast analysis and responses.
- **CORS Enabled**: Ready for integration with a separate frontend application, thanks to `Flask-Cors`.

## Tech Stack

- **Backend**: Flask
- **AI / LLM**: LangChain with Groq
- **File Processing**:
  - PyMuPDF for PDFs
  - python-docx for Word documents
  - Pytesseract for OCR
  - Pillow for image manipulation

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing.

### Prerequisites

- Python 3.8+
- Git
- **Tesseract OCR Engine**: This is a system-level dependency and must be installed separately from the Python packages.
  - **Windows**: Download and run the installer from Tesseract at UB Mannheim. Make sure to add the installation directory to your system's `PATH`.
  - **macOS**: `brew install tesseract`
  - **Linux (Debian/Ubuntu)**: `sudo apt-get install tesseract-ocr`

### Installation

1.  **Clone the repository:**
    ```sh
    git clone <your-repository-url>
    cd AI_Diagnosis
    ```

2.  **Create and activate a virtual environment:**

    *On Windows:*
    ```sh
    python -m venv myenv
    myenv\Scripts\activate
    ```

    *On macOS/Linux:*
    ```sh
    python3 -m venv myenv
    source myenv/bin/activate
    ```

3.  **Install the required Python packages:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**

    Create a file named `.env` in the project root directory and add your configuration. You will need an API key from Groq.

    ```env
    # .env

    # Flask Configuration
    FLASK_APP=app.py
    FLASK_DEBUG=True

    # Groq API Key
    GROQ_API_KEY="your-groq-api-key-here"
    ```

    *Note: The `.gitignore` file is already configured to ignore the `.env` file, so your secrets will not be committed to Git.*

## Running the Application

Once the installation is complete, you can run the Flask development server with the following command:

```sh
flask run
```

The application will be available at `http://127.0.0.1:5000`.

## API Endpoints

The primary endpoint for this application is `/diagnose` (or a similar name defined in your `app.py`).

- **URL**: `/diagnose`
- **Method**: `POST`
- **Body**: `multipart/form-data` with a single file field (e.g., `file`).
- **Success Response**: A JSON object containing the AI-generated analysis.
- **Error Response**: A JSON object with an error message.


