Backend Technical Challenge

Congratulations on reaching this stage!
We would like to thank you for the time you have dedicated to our selection process. We know that each stage requires effort, and we value the commitment you are putting into each one. Now, the time has come to demonstrate your knowledge and experience by solving this case.
This challenge aims to evaluate:

    REST API Design and clean code structure.

    Use of modern development tools in Python.

    Technical thinking and the ability to justify decisions.

    Best practices: Testing, Docker, linters, and validations.

    Estimated time: 4-6 hours. If you cannot cover everything, prioritize the core functionality and document what remains pending.

About the Challenge

Requirements:

    Language: Python

    API Framework: FastAPI

    Database: Implement a real database of your choice.

    Testing: pytest or unittest

    Linter: flake8 or pylint

    Code Formatting: black

    Docker: Configuration of a Docker container to run the application.

Details
1. Use Cases

a. Basic Use Cases:

    Create, retrieve, update, and delete task lists.

    Create, retrieve, update, and delete tasks within a list.

    Change the status of a task.

    List all tasks from a list with filters by status or priority, including an extra field indicating the completion percentage.

b. Bonus Use Cases (Optional):

    Login and Authentication: Optional implementation of JWT to protect endpoints.

    Task Assignment: Assign a responsible user to each task.

    Mock Notification: Simulation of sending an invitation to users via email (not a real email).

2. Project Structure

    Clean Architecture by layers (Domain, Application/UseCases, Infrastructure).

    Strong typing with Pydantic.

    Error handling with custom exceptions.

    Business logic validations.

    Unit and integration testing with pytest.

    Linters (flake8, ruff) and formatting (black, isort).

    Dockerfile (multi-stage if applicable) and docker-compose.

    Comprehensive README + a DECISION_LOG.md file explaining technical decisions.

3. Testing

    Implement unit and integration tests using pytest.

    Tests must cover 75% of the project.

    Include a pytest.ini file for configuration.

4. Linter and Code Formatting

    Configure flake8 as the project linter.

    Configure black as the code formatter.

    Include a .flake8 file with specific configurations (e.g., ignoring certain rules).

5. Docker

    Provide a Dockerfile to create the Docker image for the application.

    Include an optional docker-compose.yml file to facilitate running the application.

6. README

The README.md file must include:

    Project description.

    Instructions for local environment setup.

    Instructions for running the application in Docker.

    Instructions for running the tests.

Upon completion, remember to send your repository as a reply to the email.

Good luck!