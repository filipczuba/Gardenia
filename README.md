# Gardenia - Green Sharing Web Application

<div align="center">
    <img src="/media/assets/logo.png" alt="Gardenia Logo" title="Gardenia Green Sharing Platform">
   <img src="/media/assets/text.png" alt="Gardenia Logo" title="Gardenia Green Sharing Platform">
</div

## Project Overview
Gardenia is a web application designed for green sharing, allowing users to rent and share outdoor spaces like gardens and terraces. Built with Django, the platform enables property owners (Landlords) to list their spaces and renters to book them.

## Technical Stack
- **Backend**: Django Framework
- **Database**: SQLite3
- **Frontend**: 
  - HTML
  - CSS
  - JavaScript
  - Bootstrap 4
- **Additional Libraries**: 
  - Crispy Forms
  - Widget Tweaks

## Features
- User authentication with custom user roles
- Property listing and booking system
- Review and rating mechanism
- Advanced search with multiple filters
- Responsive mobile-friendly design

## Setup and Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Installation Steps
1. Clone the repository
```bash
git clone https://github.com/your-username/gardenia.git
cd gardenia
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py migrate
```

5. Create superuser
```bash
python manage.py createsuperuser
```

6. Run development server
```bash
python manage.py runserver
```

## Available Users

### 1. Administrator
- **Email**: admin@admin.com
- **Password**: password
- **Permissions**: Full system access, can manage all users, posts, and reviews


## Testing
Run test suites:
```bash
python manage.py test
```

### Test Suites
- `PostAndBookingTest`: Verifies post and booking management
- `ReviewTest`: Checks review system integrity
- `AccountsTest`: Tests user account functionalities

## Future Roadmap
- Implement geolocation search
- Add dynamic availability calendar
- Develop internal messaging system
- Create REST API for mobile application

## License
[MIT]

## Contributors
Filip Czuba
