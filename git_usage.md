# 日常操作
第一步，添加到暂存区（本地）
git add -A
第二步，添加到本地仓库更改（本地）
git commit -m "xxxxxxxxxxx备注"
第三步，同步本地仓库更改到远程（远程）
git push -u origin main

### …or create a new repository on the command line

```shell
echo "# ultralytics" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/JCRONG96/ultralytics.git
git push -u origin main
```



### …or push an existing repository from the command line

```shell
git remote add origin https://github.com/JCRONG96/ultralytics.git
git branch -M main
git push -u origin main
```

**配置名字和邮箱**
```shell
git config --global user.name "rongjc"
git config --global user.email "rongjcsz@gmail.com"
```

**查看当前代码的远程仓库链接**
```shell
git remote -v
```

**删除远程仓库连接**
```shell
git remote remove 
```

git branch -M main 是一个Git命令，用于将当前分支重命名为main。这个命令的作用是将当前分支的名称更改为main，通常用于将默认分支从旧的名称（通常是master）更改为main，以反映更加包容和多元化的编程语境。

让我解释一下这个命令的各个部分：

git branch：这是Git用于管理分支的命令。
-M：这是一个选项，它告诉Git要进行分支重命名。
main：这是你想要将当前分支重命名为的新名称。
通过运行这个命令，你可以将当前分支的名称从当前的分支名称更改为main。在执行此命令之前，确保你已经切换到了要重命名的分支。例如，如果你想将当前分支从feature-branch重命名为main，首先应该使用git checkout feature-branch切换到feature-branch，然后再运行git branch -M main来进行重命名。
