# Instructions to Create GitHub Repository Named "ai book"

## Step 1: Create the GitHub Repository

1. Go to https://github.com and log into your account
2. Click the "New" button to create a new repository
3. For the repository name, enter: `ai-book` (GitHub repositories use hyphens instead of spaces)
4. Set the repository to "Public" or "Private" as desired
5. Do NOT initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Update Remote (if needed)
If you want to change the remote name to match your new repository:

```bash
# Remove the old remote if needed
git remote remove origin

# Add the new remote with your repository name
git remote add origin https://github.com/YOUR_USERNAME/ai-book.git
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3: Push to Your New Repository
```bash
git push -u origin 001-physical-ai-robotics-textbook
```

## Alternative: Rename Repository Later
If you prefer to push first and then rename:
1. Push using the current instructions in PUSH_TO_GITHUB_INSTRUCTIONS.md
2. Go to your GitHub repository settings
3. Change the repository name to "ai-book" in the repository settings

## Note
The project content is already complete and ready. The repository name "ai-book" will be used for the remote repository on GitHub, and all your comprehensive Physical AI & Humanoid Robotics textbook content will be pushed to it.

Your complete textbook project with 9 chapters, 7 labs, and 50+ code examples will be available in your new "ai-book" repository!