# SigmaPSG

## Project Description
This project is a FastAPI application running in a Docker container, designed to provide user authentication with JWT, along with CRUD operations on user data stored in MongoDB.

## Setup Instructions

### Prerequisites
- Docker
- Docker Compose
- Python (for local development)

### Steps

1. **Clone the repository:**
    ```sh
    git clone https://github.com/trishajanath/SigmaPSG.git
    cd SigmaPSG
    ```

2. **Create a `.env` file:**
   Create a `.env` file in the root directory of the project and add your secret key and MongoDB URI:
    ```
    SECRET_KEY=uE#8r$7zD3*Q8!jN^w@1*Z8^uB5&yE0m
    MONGODB_URI=mongodb://mongo:27017
    ```

3. **Build the Docker image:**
    ```sh
    docker-compose build
    ```

4. **Start the Docker container:**
    ```sh
    docker-compose up
    ```

## Running the Application

1. **Access the application:**
    Open your web browser and go to `http://localhost:8000`.

## API Endpoints

- **POST /api/user/login**: Login a user and obtain a JWT token.
    - Request body: 
    ```json
    {
        "username": "string",
        "password": "string"
    }
    ```

- **POST /api/user**: Register a new user.
    - Request body:
    ```json
    {
        "username": "string",
        "name": "string",
        "email": "email@example.com",
        "password": "string"
    }
    ```

- **GET /api/user**: Retrieve all users.
  
- **GET /api/user/{user_id}**: Retrieve a specific user by ID.

- **PUT /api/user/{user_id}**: Update a user’s information.
    - Request body:
    ```json
    {
        "username": "string",
        "name": "string",
        "email": "email@example.com",
        "password": "string"
    }
    ```

- **DELETE /api/user/{user_id}**: Delete a user.


## Additional Information

- **Stopping the Docker container:**
    ```sh
    docker-compose down
    ```

- **Rebuilding the Docker image:**
    ```sh
    docker-compose build
    ```

## License
This project is licensed under the MIT License.
