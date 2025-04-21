group "default" {
    targets = ["react-app", "fastapi-app"]
}

target "react-app" {
    context = "./react-app"
    dockerfile = "Dockerfile"
    tags = ["react-app:latest"]
}

target "fastapi-app" {
    context = "./fastapi-app"
    dockerfile = "Dockerfile"
    tags = ["fastapi-app:latest"]
}