
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
