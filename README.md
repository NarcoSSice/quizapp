## Getting Started

To run this project, you need to have the [Docker](https://www.docker.com/).

### Installation

1. Clone the repository:

```bash
git clone https://github.com/NarcoSSice/quizapp
```

2. Run the docker-compose:

```bash
docker-compose up --build 
```

3. Make migrations:

```bash
docker-compose run --rm quizapp_service alembic upgrade head
```