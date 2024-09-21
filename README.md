# Demo Application to Showcase the Arcane Dev Kit

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-3.2%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Project Description
This is a demo project to showcase the capabilities of the Arcane Engine, a platform that enables developers to create powerful tools and automations for their teams.

## 🛠️ Tech Stack
- **Backend**: Python and Django
- **Frontend**: Django templates, BulmaCSS, and jQuery

## 📂 Project Structure

### Pull Request Manager
A simple demo that lists all PRs of all repos you have access to on Github and lets you generate PR descriptions in seconds.
- **Code**: `pr_manager/`
- **Template**: `pr_manager/templates/index.html`
- **Views**: `pr_manager/views.py`
- **URLs**: `pr_manager/urls.py`

### Tasks Manager
A simple demo that lists all tasks of all repos you have access to on Github and lets you create new tasks.
- **Code**: `tasks/`
- **Templates**: `tasks/templates/`
- **Views**: `tasks/views.py`
- **URLs**: `tasks/urls.py`

### Reports
Lets users generate reports based on prompts.
- **Code**: `reports/`
- **Templates**: `reports/templates/`
- **Views**: `reports/views.py`
- **URLs**: `reports/urls.py`
- **Models**: `reports/models.py`

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Django 3.2+

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/arc-eng/demo.git
   ```
2. Navigate to the project directory:
   ```sh
   cd demo
   ```
3. Install the dependencies:
   ```sh
   poetry install
   ```
4. Apply migrations:
   ```sh
   python manage.py migrate
   ```
5. Run the development server:
   ```sh
   python manage.py runserver
   ```

## 🤝 Contributing
Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) first.

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📧 Contact
For any inquiries, please contact us at [support@arcane.dev](mailto:support@arcane.dev).