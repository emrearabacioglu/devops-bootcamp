
<details>
<summary>Exercise 0: Clone Git Repository </summary>
 <br />

* Clone the git repository and
* Create your own project/git repo from it

**steps:**

```sh
# clone repository & change into project dir
git clone git@gitlab.com:twn-devops-bootcamp/latest/05-cloud/cloud-basics-exercises.git
cd node-project

# removed remote repo reference and create own local repository
rm -rf .git
git init 
git add .
git commit -m "initial commit"

# created git repository on Github and pushed newly created local repository to it
git remote add origin git@github.com:emrearabacioglu/cloud-exercises.git
git push -u origin master

```

</details>

******


<details>
<summary>EXERCISE 1: Package NodeJS App </summary>
 <br />
To have just 1 file, you create an artifact from the Node App. So you do the following:

* Package your Node app into a tar file (npm pack)

  **steps**

```sh
cd app
npm pack

```


 </details>

******

<details>
<summary>EXERCISE 2: Create a new server </summary>
 <br />

* Create a new droplet server on DigitalOcean

  <img width="1224" height="301" alt="image" src="https://github.com/user-attachments/assets/2f84d6bc-559a-4e50-aab5-8bc3574ca697" />


  </details>

******


<details>
<summary>EXERCISE 3: Prepare server to run Node App </summary>
 <br />

* Install nodejs & npm on it

  **steps:**
```sh

apt update
apt install nodejs
apt install npm

```

  </details>

******  


<details>
<summary>EXERCISE 4: Copy App </summary>
 <br />

* Copy your simple Nodejs app to the droplet

**steps:**
```bash
$ scp bootcamp-node-project-1.0.0.tgz root@161.35.25.127:/root
bootcamp-node-project-1.0.0.tgz               100%   78KB 465.7KB/s   00:00

```

  </details>

******

<details>
<summary>EXERCISE 5: Run Node App </summary>
 <br />
 
* Start the node application in detached mode (npm install and node server.js commands)
**steps:**

```sh
tar -zxvf bootcamp-node-project-1.0.0.tgz
npm install
node server.js 
```
  </details>

******


<details>
<summary>EXERCISE 6: Access from browser - configure firewall </summary>
 <br />

* Open the correct port on Droplet
* Access the UI from browser

**steps**
```sh
node server.js &
ps aux | grep node
netstat -lnpt
```
app listening on port 3000!


<img width="801" height="720" alt="image" src="https://github.com/user-attachments/assets/79ddbf11-2b0b-4602-be2e-ae1f39f27b7f" />


  </details>

******


