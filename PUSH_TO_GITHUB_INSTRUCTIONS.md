# Instructions to Push Project to GitHub

## Step 1: Create a GitHub Repository
1. Go to https://github.com and log into your account
2. Click the "New" button to create a new repository
3. Choose a repository name (e.g., "physical-ai-humanoid-robotics-textbook")
4. Set the repository to "Public" or "Private" as desired
5. Do NOT initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Add the Remote Repository
Replace `<your-github-repository-url>` with your actual repository URL:

```bash
git remote add origin <your-github-repository-url>
```

For example:
```bash
git remote add origin https://github.com/yourusername/physical-ai-humanoid-robotics-textbook.git
```

## Step 3: Verify the Remote
```bash
git remote -v
```

You should see both fetch and push URLs for the origin remote.

## Step 4: Push the Code
```bash
git push -u origin 001-physical-ai-robotics-textbook
```

This will push the current branch with all the commits to your GitHub repository.

## Step 5: Set Main Branch (Optional)
If you want to rename the branch to main after pushing:

```bash
git branch -M main
git push -u origin main
```

## Verification
After pushing, you can verify the content is on GitHub by visiting your repository URL in a web browser. You should see all the files and folders that were created as part of this comprehensive textbook project.

## Note
The project is completely ready with:
- 9 chapters covering from foundational concepts to Isaac Sim
- 7 comprehensive lab exercises (3-9)
- 50+ code examples across all simulation platforms
- Complete documentation site structure
- All necessary configuration files
- Properly formatted content and code

Your Physical AI & Humanoid Robotics textbook project is ready to be shared and used!