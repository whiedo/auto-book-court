<h1>Documentation</h1>

<h2>Downloads:</h2>
-Python for Windows
-VSCode w/ Python/Docker extension
-Docker for Desktop
-Git for Windows

<h2>VSCode/Git:</h2>
git init
git add --all
git config --global user.email f_elix@web.de
git config --global user.name Felix
git commit -m "inital commit"
git remote add origin https://github.com/whiedo/auto-book-court.git
git branch -M master
git push --set-upstream origin master

<h2>Python:</h2>
pip install requests/selenium

<h2>Docker:</h2>
docker pull jenkins/jenkins
docker run -d -v jenkins_home:/var/jenkins_home -p 8080:8080 -p 50000:50000 --restart=on-failure jenkins/jenkins
docker logs goofy_rosalind

<h2>Jenkins:</h2>
Jenkins-URL: http://localhost:8080/
Jenkins-Docker-Container-Adm: admin, de651299ddca40499db183672dea7350
Add new Multibranch Pipeline
-Add GitHub credentials and GitHub repository
Settings -> Plugins -> Install docker pipelines/Blueocean