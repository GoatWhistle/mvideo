variable "COMPOSE_PROJECT_NAME" {
  default = "app"
}

variable "TAG" {
  default = "latest"
}

variable "LLM" {
  default = "false"
}

variable "SITE_URL" {
  default = ""
}

group "default" {
  targets = ["backend", "frontend"]
}

target "backend" {
  context = "backend"
  args = {
    LLM = LLM
  }
  tags = ["${COMPOSE_PROJECT_NAME}-backend:${TAG}"]
  output = ["type=docker"]
}

target "frontend" {
  context = "frontend"
  args = {
    SITE_URL = SITE_URL
  }
  tags = ["${COMPOSE_PROJECT_NAME}-frontend:${TAG}"]
  output = ["type=docker"]
}

variable "REGISTRY" {
  default = "registry.vm/dev"
}

group "homelab" {
  targets = ["backend-homelab", "frontend-homelab"]
}

target "_homelab" {
  platforms = ["linux/amd64"]
  output    = ["type=docker"]
  labels = {
    "org.opencontainers.image.version" = "${TAG}"
    "org.opencontainers.image.source"  = "https://github.com/GoatWhistle/mvideo"
  }
}

target "backend-homelab" {
  inherits = ["backend", "_homelab"]
  tags     = ["${REGISTRY}/mvideo-backend:${TAG}", "${REGISTRY}/mvideo-backend:latest"]
  labels   = { "org.opencontainers.image.title" = "mvideo-backend" }
}

target "frontend-homelab" {
  inherits = ["frontend", "_homelab"]
  tags     = ["${REGISTRY}/mvideo-frontend:${TAG}", "${REGISTRY}/mvideo-frontend:latest"]
  labels   = { "org.opencontainers.image.title" = "mvideo-frontend" }
}
