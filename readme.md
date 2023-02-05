Downloads:
-Python for Windows
-VSCode w/ Python/Docker extension
-Docker for Desktop
-Git for Windows

Docker:
docker pull jenkins/jenkins
docker run -d -v jenkins_home:/var/jenkins_home -p 8080:8080 -p 50000:50000 --restart=on-failure jenkins/jenkins
docker logs goofy_rosalind

Jenkins:
Jenkins-URL: http://localhost:8080/
Jenkins-Docker-Container-Adm: admin, de651299ddca40499db183672dea7350
Add new Multibranch Pipeline