POWERSHELL

in docker_configuration folder:

1. $env:PWD_PARENT = (Get-Item -Path ".\").Parent.FullName; docker-compose up --build --detach 

2. docker ps -a --filter "name=docker_configuration" --format "{{.ID}}"

3. use output ID for command : docker cp ID:/app/docker-compose.yml (Get-Item -Path ".\").Parent.FullName
example: docker cp aa2dd076eed7:/app/docker-compose.yml (Get-Item -Path ".\").Parent.FullName

4. cd ..

5. Get-Content -Path .\docker-compose.yml | Out-File -FilePath ".\wiki\docker-compose.txt"

5. docker-compose up --build --detach

